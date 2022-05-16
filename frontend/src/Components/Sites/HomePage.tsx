import '../../App.css'
import ReactDOM from "react-dom";
import { applicationState, requestArgs } from '../../ApplicationModel/ApplicationState.model';
import { formatter } from '../Graphs/GraphLogic';
import { populateOptimizationView } from '../Graphs/GraphPopulation';
import { NavBar } from '../Navigation/NavBar';
import { sendRequest } from '../../Services/Common';
import { CustomizationOptions } from '../Navigation/Customizationoptions';
import { DeploymentOptions } from '../Navigation/DeploymentOptions';
import { useState } from 'react';
import { defaultState } from '../../State/DefaultApplicationState';
import Title from "antd/lib/typography/Title";
import { Row, Col } from 'antd';

function getTotalComputation(data: string): string {
	return JSON.parse(JSON.stringify(data))['versions']['stats']['app_computation'];
}

async function getData(args: requestArgs): Promise<string> {
	const res = await sendRequest(args.arg1, args.arg2, args.arg3); //normal docs: date_from, date_to, false. deployment docs: type, key, true.

	console.log("Received time:" + Date.now())
	const answer = await res.json()
	if (typeof answer === "string") {
		if (answer.startsWith('Data missing')) {
			alert(answer);
		}

		return JSON.parse(answer);
	}
	else {
		return JSON.parse(JSON.stringify(answer));
	}
}

async function getDeploymentDocsList(): Promise<string[]> {
	const res = await sendRequest('list', '', true);
	const f: string[] = JSON.parse(await res.json())//.concat(['test']);

	return f
}

function HomePage() {

	const [state, setState] = useState(defaultState)
	const UpdateState = (props: {
		changes: Partial<applicationState>
	}) => {
		return setState({ ...state, ...props.changes })
	}

	if (state.content === false) {
		// Show frontend input fields
		if (state.availableDeploymentDocumentation.length === 0) {

			getDeploymentDocsList().then(availableDeploymentDocumentation => { UpdateState({ changes: { availableDeploymentDocumentation } }) })
		}

		//;

		return <body>
			<div className='rowParent' >
				<Row justify="center">
					<Title level={1}>Choose A Method To Obtain<br />Runtime Documentation</Title>
				</Row>
				<Row justify="center" align="middle" className='row'>
					<Col span={10} offset={0}>
						<CustomizationOptions
							state={state}
							updateData={(args: requestArgs) => {
								getData(args).then(r => {
									UpdateState({ changes: { content: r } })
								})
							}}
						/>
					</Col>
					<Col span={2} offset={0}>
						<Title level={1} >- OR -</Title>
					</Col>
					<Col span={10} offset={0}>
						<DeploymentOptions
							state={state}
							onclickEvent={(s: requestArgs) => {

								getData(s).then(r => { UpdateState({ changes: { content: r } }) })
							}}
						/>
					</Col>
				</Row>
				<Row justify="center" className='bottomRow'>
					<Col span={10}>
						<Title level={3}>Enter a time range.</Title>
						<Title level={5}>The range will determine the scope of the documentation.</Title>
					</Col>
					<Col span={2}>
					</Col>
					<Col span={10}>
						<Title level={3}>Select an application state.</Title><br/>
						<Title level={5}>The beginning and end of these states is marked by detected deployments.</Title>
					</Col>
				</Row>

			</div>
		</body>;
	}
	//Otherwise show the graph
	const data = populateOptimizationView(state.content);
	const requestArchitectureGraph = formatter(state.content, false, false, false, false);
	const architectureUsageGraph1 = formatter(state.content, true, false, true, false);
	const architectureUsageGraph2 = formatter(state.content, false, true, false, false);
	const startupGraph = formatter(state.content, false, false, true, true);

	if (state.architectureUsageGraph1.edges.length === 1) {
		UpdateState({
			changes: {
				requestArchitectureGraph,
				architectureUsageGraph1,
				architectureUsageGraph2,
				barGraph: { data },
				startupGraph
			}
		})
	}

	return (
		<>
			<NavBar
				state={state}
			/>

		</>
	);
}

const rootElement = document.getElementById("root");
ReactDOM.render(<HomePage />, rootElement);

export default HomePage;