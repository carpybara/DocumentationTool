import { Button, DatePicker, Layout, message, Radio, Space } from "antd";
import moment from "moment";
import { applicationState } from "../../ApplicationModel/ApplicationState.model";

export const CustomizationOptions = (props: {
  state: applicationState
  updateData: any
})=>{
return <>

		<div className="configuration">
		<Space direction="vertical">
    <DatePicker 
			onChange={date => {
				props.state.datestate.from = moment(date?.format("YYYYMMDD").toString()).unix() ?? 0;

					}} />
    <DatePicker 
			onChange={date => {
        props.state.datestate.fromGran = moment(date).unix() - moment(date?.format("YYYYMMDD").toString()).unix() ?? 0;
					}}
			picker="time" 
		/>
  </Space>
	<Space direction="vertical">
    <DatePicker onChange={date => {
						props.state.datestate.to = moment(date?.format("YYYYMMDD").toString()).unix() ?? 0;
						//console.log("to time: " + String(props.state.datestate.to))
					}} />
    <DatePicker 			
			onChange={date => {
				props.state.datestate.toGran = moment(date).unix() - moment(date?.format("YYYYMMDD").toString()).unix() ?? 0;
					}} 
			picker="time" 
		/>
  </Space>
			<div>
				<Button
					type="primary"
					onClick={() => {

						const info = () => {
							message.info('Please select a valid time range');
						};
						if(props.state.datestate.from + props.state.datestate.fromGran > props.state.datestate.to + props.state.datestate.toGran){
							return info()
						}
						if(props.state.datestate.from === 0 || props.state.datestate.to === 0){
							return info()
						}
						console.log("Sent time:" + Date.now());
						const args = {arg1: props.state.datestate.from + props.state.datestate.fromGran, arg2: props.state.datestate.to + props.state.datestate.toGran, arg3: false};
						props.updateData(args);
					}}
				
				>
					Fetch &amp; Generate
				</Button>
			</div>
		</div>



</>
}