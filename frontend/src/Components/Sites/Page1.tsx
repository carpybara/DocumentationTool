import { Layout } from "antd";
import Title from "antd/lib/typography/Title";
import { applicationState } from "../../ApplicationModel/ApplicationState.model";
import { Tree } from "../Graphs/Graphs";

function Page1(state: applicationState) {
  console.log("Displayed time:" + Date.now())
  return (
      <Layout>
        <Title level={1} className='graphTitle'>Overview</Title>
        <Title level={3} className='graphTitle'>Request Architecture</Title>
        <div className='GraphBorder'>
          <Tree
            graphData={state.requestArchitectureGraph}
            containsAdditionalElement={true}
            content={state.content}
            edgeProps={{
              edges: {
                color: "#000000",
                smooth: {
                  type: 'discrete',
                  roundness: 0.7
                },
                length: 600,
                scaling: {
                  min: 1,
                  max: 1 // to avoid scaling in first graph.
                },
                arrowStrikethrough: false,

                physics: false //false gets rid of the animation
              }
            }}
            nodeProps={{
              nodes: {
                shape: 'dot',
                opacity: 1,
                color: {
                  background: 'rgba(210, 229, 255,1)',
                },
                widthConstraint: 120, //necessary
              }
            }}
            sizeProps={{
              height: "700px",
            }}
            />
        </div>
        <Title level={5} className='graphTitle'>Click on function nodes or hover over edges and nodes.</Title>
      </Layout>
  );
  
}

export default Page1;