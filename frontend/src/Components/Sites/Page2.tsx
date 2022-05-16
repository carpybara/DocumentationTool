import Title from "antd/lib/typography/Title";
import { applicationState } from "../../ApplicationModel/ApplicationState.model";
import { populateTotalLambdaCosts } from "../Graphs/GraphPopulation";
import { PieChart, Tree } from "../Graphs/Graphs";
import { makeInitList } from "../Graphs/GraphLogic";
import { Layout, Divider, Table } from "antd";

function Page2(state: applicationState) {
  if (state.content === false) {
    return <>Internal Error. State.content was not defined</>
  }
  const functionTotalCompute = populateTotalLambdaCosts(state.content);
  const initDurationList = makeInitList(state.content);
  const initProps = {
    bordered: true,
  }
  const initColumns = [
    {
      title: 'Function Name',
      dataIndex: 'funcName'
    },
    {
      title: 'Average Init Duration (ms)',
      dataIndex: 'initDuration'
    }
  ]
  return (
    <div>
      <Layout>
        <Title level={1} >Optimization</Title>
        <Title level={3} >Function Performance &amp; Traffic</Title>
        
        <div className='GraphBorder'>
          {<Tree
            containsAdditionalElement={false}
            graphData={state.architectureUsageGraph1}

            edgeProps={{
              edges: {
                color: "#000000",
                smooth: {
                  type: 'discrete', //discrete ok, horizontal ok, diagonalCross and curvedCCW with low roundness ok
                  roundness: 0.7
                }, //helps detect edge overlap
                length: 600,
                scaling: {
                  min: 0.01,
                  max: 10
                },
                arrowStrikethrough: false, //important to see arrow head when edge wide
                physics: false //false gets rid of the animation
              }
            }}

            nodeProps={{
              nodes: {
                shape: 'dot',
                widthConstraint: 120, //necessary
              }
            }}
            sizeProps={{
              height: "700px",
            }}
          />}
        </div>
        

        <div className='my-legend'>
          <div className='legend-title'>Comparative Function Performance</div>
          <div className='legend-scale'>
            <ul className='legend-labels'>
              <li><span className="superawesome"></span>0 - 20%</li>
              <li><span className="awesome"></span>40%</li>
              <li><span className="kindaawesome"></span>60%</li>
              <li><span className="almostnotawesome"></span>80%</li>
              <li><span className="notawesome"></span>100%</li>
              <li><span className="invalid"></span>N/A</li>
            </ul>
          </div>
        </div>


        <div id='ComputeWrapper'>
          <div id='ComputeGraphElement'>
            <Title level={3} >Function Compute Graph</Title>
            
            <div className='GraphBorder'>
              <Tree
                containsAdditionalElement={false}
                graphData={state.architectureUsageGraph2}
                edgeProps={{
                  edges: {
                    color: "#000000",
                    smooth: {
                      type: 'diagonalCross', //discrete ok, horizontal ok, diagonalCross and curvedCCW with low roundness ok
                      roundness: 0.5
                    }, //helps detect edge overlap
                    length: 600,
                    scaling: {
                      min: 1,
                      max: 1
                    },
                    arrowStrikethrough: false, //important to see arrow head when edge wide
                    physics: false //false gets rid of the animation
                  }
                }}
                nodeProps={{
                  nodes: {
                    shape: 'dot',
                    widthConstraint: 120, //necessary
                    scaling: {
                      min: 15,
                      max: 50,
                      label: {
                        enabled: false
                      }
                    }
                  }
                }}
                sizeProps={{
                  height: "700px",
                  width: "1000px"
                }}
              />
            </div>
          </div>

          <div id='pieView'>
            <Title level={3}>Total Lambda Compute</Title>
            <PieChart
              graphdata={functionTotalCompute}
            />
          </div>
        </div>

        <Divider />

        <Title level={2}>Startup</Title>

        <div id='startupWrapper'>
          <div id='startupGraphElement'>
            <Title level={3}>Init Duration &amp; Used Lambda Layers</Title>
            <Title level={5}>Hover over function nodes to see its used layers.</Title>
            <div className='GraphBorder'>
              <Tree
                containsAdditionalElement={false} //but needs something similar, just with different data
                graphData={state.startupGraph}
                edgeProps={{
                  edges: {
                    color: "#000000",
                    smooth: {
                      type: 'discrete', //discrete ok, horizontal ok, diagonalCross and curvedCCW with low roundness ok
                      roundness: 0.7
                    }, //helps detect edge overlap
                    length: 600,
                    scaling: {
                      min: 1,
                      max: 1
                    },
                    arrowStrikethrough: false, //important to see arrow head when edge wide
                    physics: false //false gets rid of the animation
                  }
                }}
                nodeProps={{
                  nodes: {
                    shape: 'dot',
                    widthConstraint: 120, //necessary
                  }
                }}
                sizeProps={{
                  height: "700px",
                  width: "1000px"
                }}
              />
            </div>
          </div>


          <Title level={3} >Init Duration per Function</Title>
          <Title level={5} >Consult the init durations for further information.</Title>
          <div id='initListParent'>
            <div id='initGraphElement'>
              <Table dataSource={initDurationList} columns={initColumns} {...initProps} />
            </div>
          </div>

        </div>
      </Layout>
    </div>
  );
}

export default Page2;