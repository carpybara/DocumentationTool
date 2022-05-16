import Graph from "react-graph-vis";
import { Typography } from "antd";
import { applicationState, graphstate } from "../../ApplicationModel/ApplicationState.model";
import { each, groupBy } from '@antv/util';
import { populateVersionView } from "../Versioning/VersioningGraph";
import { orderedTimes } from "../Versioning/versioning.model";
import { keyOf } from "../../Services/Common";
import { Line, Pie, Column } from "@ant-design/plots";
import ReactDOM from "react-dom";

const { Text } = Typography;

const events = {
  select: function (event: { nodes: any; edges: any; }) {
    var { nodes, edges } = event;
  }
};

const baseOptions = {
  layout: {
    improvedLayout: true,
  },
  physics: {
    enabled: true,
    barnesHut: {
      avoidOverlap: 1,
      springLength: 140
    },
    solver: 'barnesHut'
  },

  interaction: {
    dragView: true,
    dragNodes: true,
    keyboard: false,
  },
  //height: "700px",
  //width: "1000px"
}




export const Tree = (props: {
  readonly edgeProps: any
  readonly nodeProps: any
  readonly sizeProps: any
  readonly graphData: graphstate
  readonly containsAdditionalElement: false

} | {
  readonly edgeProps: any
  readonly nodeProps: any
  readonly sizeProps: any
  readonly graphData: graphstate
  readonly containsAdditionalElement: true
  readonly content: applicationState['content']
} ) => {
    return <Graph
    graph={props.graphData} // this is without levels
    options={{
      ...baseOptions,
       ...props.edgeProps,
       ...props.nodeProps,
       ...props.sizeProps,
      }}
    events={events}
    getNetwork = {props.containsAdditionalElement === true ? (network: any) => { network.on("selectNode", function(this:any, params:any){ //trying this here
      var selectedNodeID = params.nodes;
      var selectedNode = this.body.nodes[selectedNodeID];
      var versionViewDataNEW:orderedTimes[] = populateVersionView(props.content, selectedNode.options.label);
      //var statsPerVersion = getInfoPerVersion(props.content, selectedNode.options.label)
      if (versionViewDataNEW.length===1 && versionViewDataNEW[0].version===''){return 0;}
      


      var config = {
        data: versionViewDataNEW,
        xField: keyOf<orderedTimes>('timeRange'),
        yField: keyOf<orderedTimes>('value'),
        seriesField: keyOf<orderedTimes>('version'),
        point: {},
        xAxis: {
          label: {
            formatter: (v: any) => v
          },
          //tickInterval: 1
          //type: 'time', 
          tickMethod: 'cat',
          //tickCount: 5
        },
        yAxis: {
          title: {
            text: "Number of Invocations",
            style: {
              fontSize: 16
            }
          },
          label: {
          formatter: (v: any) => `${v}`.replace(/\d{1,3}(?=(\d{3})+$)/g, (s) => `${s},`),
          },
        },
      };
      var graphPopUp = document.createElement("div");
      selectedNode.options.title = graphPopUp

      return ReactDOM.render(
        <>
        <Text strong>Version Activity: {selectedNode.options.label}</Text>
        <Line {...config}/>
        
        </>,
        graphPopUp
      );
      
    })
    }: undefined}
    />
  }


export const PieChart = (props: {
  readonly graphdata: Object[]
}) => {

  return <Pie
  data = {props.graphdata}
  appendPadding= {10}
  angleField = {'value'}
  colorField = {'functionName'}
  radius = {0.6}
  label = {{
    type: 'outer',
    content: '{percentage}',
  }}
  interactions = {[
    {
    type: 'element-active',
    },
    {
    type: 'element-selected',
    },
  ]}
  />
}


export const BarGraph = (props: {
  graphData: any
}) => {
  
  // Based on: https://charts.ant.design/en/examples/column/stacked#annotation-label
  const annotations = [] as any;
	each(groupBy(props.graphData, 'FunctionName'), (values, k) => {
	  const Value = Math.round(values.reduce((a: any, b: any) => a + b.Value, 0));
	  annotations.push({
		type: 'text',
		position: [k, Value],
		content: `${Value}MB`,
		style: {
		  textAlign: 'center',
		  fontSize: 15,
		  fill: 'rgba(0,0,0,0.85)',
		},
		offsetY: -10,
	  });
	});

  return <Column
    data = {props.graphData}
    width = {100}
    xField = {'FunctionName'}
    yField = {'Value'}
    seriesField = {'StatType'}
    isStack = {true}
    label = {{
		  position: 'top' as 'top',
		  //style: {
			//fill: '#fff',
		  //},
		  layout: [
			{
			  type: 'interval-adjust-position',
			},
			{
			  type: 'interval-hide-overlap',
			},
			{
			  type: 'adjust-color',
			},
		  ],
		}}
    annotations = {annotations}
  />
}


