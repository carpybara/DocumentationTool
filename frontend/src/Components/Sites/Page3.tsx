import { Layout, Divider, Table } from "antd";
import Title from "antd/lib/typography/Title";
import { applicationState } from "../../ApplicationModel/ApplicationState.model";
import { populateOptimizationView } from "../Graphs/GraphPopulation";
import { BarGraph } from "../Graphs/Graphs";
import { populateTimeoutList } from "../Timeouts/TimeoutView";

function Page3(state: applicationState) {
  if (state.content === false) {
    return <>Content was not defined</>
  }
  const functionTimeouts = populateTimeoutList(state.content);
  const timeoutColumns = [
    {
      title: "Function Name",
      dataIndex: "funcName"
    },
    {
      title: "Timeout (s)",
      dataIndex: "timeout"
    }
  ]
  const timeoutProps = {
    bordered: true,
  }
  const data = populateOptimizationView(state.content);

  return (
    <div>
      <Layout>
        <Title level={1} className='graphTitle'>Configuration</Title>
        <Title level={3} className='graphTitle'>Configured and Max. Used Memory by Function</Title>
        <Title level={5} className='graphTitle'>Find out about possible misconfiguration.</Title>
        <div style={{ width: '80%', margin: '0 auto' }}>
          <BarGraph
            graphData={data}
          />
        </div>

        <Divider/>

        <Title level={3} className='graphTitle'>Configured Function Timeouts</Title>
        <Title level={5} className='graphTitle'>Consult a list of the function timeouts of the application.</Title>
        <div style={{ width: '80%', margin: '0 auto' }}>
          <Table dataSource={functionTimeouts} columns={timeoutColumns} {...timeoutProps}/>
        </div>
      </Layout>
    </div>
  );
}

export default Page3;