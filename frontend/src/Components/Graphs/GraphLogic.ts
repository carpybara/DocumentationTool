import { applicationState, Edge, Node } from "../../ApplicationModel/ApplicationState.model";
import { getStartupData } from "../Startup/StartupInfo";

export function formatter(data: string, isColoredPerformance: Boolean, isSized: Boolean, withEdgeCount: Boolean, isColoredStartup: Boolean): applicationState['requestArchitectureGraph'] {
	const dataDict = JSON.parse(JSON.stringify(data))


	if (Object.keys(dataDict).length !== 2) {
		if (dataDict.includes("Data missing")){
			alert('Data is missing for these dates. We will fix this immediately.\nTry again in 1 minute.');
		}
		console.error('Incorrect data format')
	}

	const inventory = dataDict["inventory"];
	const versioning = dataDict["versions"];

	const scale = JSON.parse(JSON.stringify(performanceToColor(versioning, true)));
	const computationDict = JSON.parse(JSON.stringify(calcSize(versioning)));
	const startupData = getStartupData(dataDict);
	const startupScale = JSON.parse(JSON.stringify(performanceToColor(startupData, false)));

	const uniqueInteractions = inventory

	const MyNodes = [] as Node[];
	const MyEdges = [] as Edge[];
	var counter = 0;
	const ServiceIDs = {} as any;


	for (let key in uniqueInteractions) {

		if (MyNodes.find((element: { label: string; }) => element.label === uniqueInteractions[key]["source"]) === undefined) {

			MyNodes.push({
				id: counter,
				label: uniqueInteractions[key]["source"],
				//if there's sizing, show total computation. else if there's coloring show performance, else undefined
				title: isSized && (uniqueInteractions[key]["source"] in computationDict) ? computationDict[uniqueInteractions[key]["source"]]+"GB-s" : isColoredPerformance &&  (uniqueInteractions[key]["source"] in versioning) ? versioning[uniqueInteractions[key]["source"]]['stats']['func_avg_billedDuration'].toFixed(2)+"ms" : isColoredStartup ? getLayers(startupData, uniqueInteractions[key]["source"]) : undefined,
				color: isColoredPerformance ? { background: assignColor(scale[uniqueInteractions[key]["source"]]) } : isColoredStartup ? { background: assignColor(startupScale[uniqueInteractions[key]["source"]]) } : undefined,
				value: isSized ? computationDict[uniqueInteractions[key]["source"]] : undefined,
			});
			ServiceIDs[uniqueInteractions[key]["source"]] = counter;
			counter++;
		}

		if (MyNodes.find((element: { label: string; }) => element.label === uniqueInteractions[key]["terminus"]) === undefined) {

			MyNodes.push({
				id: counter,
				label: uniqueInteractions[key]["terminus"],
				//if there's sizing, show total computation. else if there's coloring show performance, else show terminus_location
				title: isSized && (uniqueInteractions[key]["terminus"] in computationDict) ? computationDict[uniqueInteractions[key]["terminus"]] +"GB-s" : isColoredPerformance &&  uniqueInteractions[key]["terminus"] in versioning ? versioning[uniqueInteractions[key]["terminus"]]['stats']['func_avg_billedDuration'].toFixed(2) + "ms" : isColoredStartup ? getLayers(startupData, uniqueInteractions[key]["terminus"]) : uniqueInteractions[key]["terminus_location"],
				color: isColoredPerformance ? { background: assignColor(scale[uniqueInteractions[key]["terminus"]]) } : isColoredStartup ? { background: assignColor(startupScale[uniqueInteractions[key]["terminus"]]) } : undefined,
				value: isSized ? computationDict[uniqueInteractions[key]["terminus"]] : undefined
			});
			ServiceIDs[uniqueInteractions[key]["terminus"]] = counter;
			counter++;
		}

		MyEdges.push({
			from: ServiceIDs[uniqueInteractions[key]["source"]],
			to: ServiceIDs[uniqueInteractions[key]["terminus"]],
			value: uniqueInteractions[key]["count"],
			title: withEdgeCount ? +uniqueInteractions[key]["count"] : uniqueInteractions[key]["via"], //or "count"
			//label: String(uniqueInteractions[key]["count"]),
			//font: { align: "middle" }
		});
		

	}
	const MyGraph = {
		nodes: MyNodes,
		edges: resolveDuplicateEdges(MyEdges, withEdgeCount)
	};
	return MyGraph;
}

function resolveDuplicateEdges( edges : Edge[], isCount : Boolean) : Edge[]{
	var edgeSet = {} as any;

	for (let i=0; i < (edges.length); i++) {
		let keyName = String(edges[i]['to']) + "|" + String(edges[i]['from']);
		if (keyName in edgeSet){
			edgeSet[keyName]['value'] += edges[i]['value'];
			
			if (isCount) {
				edgeSet[keyName]['title'] = edgeSet[keyName]['value'];
			}
			else if (isCount===false) {	
				edgeSet[keyName]['title'] = String(edgeSet[keyName]['title']) + "|" + String(edges[i]['title']);
			}
		}
		else {
			edgeSet[keyName] = edges[i];
			//differentiate between count and via, string and number
		}
	}

	//Rebuild Edge[] from dict
	var result:Edge[] = [];
	for (let key in edgeSet){
		result.push(edgeSet[key]);
	}

	return result;
}


function performanceToColor(data: string, isPerformance: Boolean): { [funcName: string]: number } {
	const versioningDict = JSON.parse(JSON.stringify(data))
	const mapping: { [funcName: string]: number } = {}; //Duggo halp
	const valueRange = [] as number[];
	const functionLatestVersion = {} as any;

	if (isPerformance){
		// Go to function level, get relevant stats, assign performance score 1-100 
		for (let key in versioningDict) {
			//case: everything except the total stats object
			if (key !== "stats") {
				//Using allocated memory
				const avgDuration = versioningDict[key]['stats']['func_avg_billedDuration']; //in ms
				const versions = Object.keys(versioningDict[key]).filter(item => item!=="stats");
				const latestVersion = findLargestNumber(versions);
				functionLatestVersion[key] = latestVersion;

		
			valueRange.push(avgDuration); //performance is only based on duration.
			}
		}
	}
	else {
		for (let key in versioningDict) {
			valueRange.push(versioningDict[key]['current_avg_initDuration']);		
		}
	}

	const sortedValues = valueRange.sort((n1, n2) => n1 - n2);
	const old_bottom = sortedValues[0];
	const old_top = sortedValues[sortedValues.length - 1];
	//the below determines the range of our grades
	const new_bottom = 1;
	const new_top = 100;

	if (isPerformance){
		for (let key in versioningDict) {
			if (key !== "stats") {
				let versionDataLength = versioningDict[key][functionLatestVersion[key]].length;
				let memorySize = versioningDict[key][functionLatestVersion[key]][versionDataLength - 1]['version_memorySize'] / 1000000000;
				let old_value = (versioningDict[key]['stats']['func_avg_billedDuration']); //* memorySize; //ms
				let new_value = (((old_value - old_bottom) / (old_top - old_bottom)) * (new_top - new_bottom)) + new_bottom;
				mapping[key] = Math.round(new_value * 100)/100;
			}
		}
	}
	else {
		for (let key in versioningDict) {
			let old_value = (versioningDict[key]['current_avg_initDuration']); //* memorySize; //ms
			let new_value = (((old_value - old_bottom) / (old_top - old_bottom)) * (new_top - new_bottom)) + new_bottom;
			mapping[key] = Math.round(new_value * 100)/100;
			}
		}
	
	
	return mapping;
}

function calcSize(data: string): { [funcName: string]: number } {
	const versioningDict = JSON.parse(JSON.stringify(data));
	const mapping: { [funcName: string]: number } = {};

	for (let key in versioningDict) {
		if (key !== 'stats') {
			mapping[key] = Math.round(Number(versioningDict[key]['stats']['func_total_computation'])*100)/100;
		}
	}
	return mapping;
}

function assignColor(value: number): string {
	if (value > 0 && value <= 20) {
		return "#52c41a";
	}
	if (value > 20 && value <= 40) {
		return "#a0d911";
	}
	if (value > 40 && value <= 60) {
		return "#fadb14";
	}
	if (value > 60 && value <= 80) {
		return "#faad14";
	}
	if (value > 80 && value <= 100) {
		return "#fa8c16";
	}

	else {
		return "rgba(255, 255, 255,1)"; //return white
	}
}

export function findLargestNumber(array:string[]) : number{
	let numArray = [] as number[];
	array.forEach(str => {
		numArray.push(Number(str));
	  });

	return numArray.sort((a,b)=>a-b)[numArray.length - 1];
}


function getLayers(data:string, funcName:string) {
	const startupDict = JSON.parse(JSON.stringify(data))
	if(!(funcName in startupDict)){
		return undefined;
	}

	var functionLayerString:string = "Layers\n";
	//get layers for a specific function from the dict and put into a useful format.
	const layers = startupDict[funcName]['layers'];
	if(layers.length===0){
		functionLayerString = "No Layers Used";
	}
	else {
		for (let i=0; i<layers.length; i++){
			var layerName = String(layers[i]['name']);
			var layerSize = String(layers[i]['size']);
			functionLayerString = functionLayerString + layerName + ": " + layerSize + "MB\n";
		}
	}
	
	return functionLayerString;
}


export function makeInitList(data:string) :[]{
	const startupDict = getStartupData(JSON.parse(JSON.stringify(data)));
	const resultList:any = [];

	for(let funcName in startupDict){
		resultList.push({
			'funcName': funcName,
			'initDuration': startupDict[funcName]['current_avg_initDuration'].toFixed(2)
		})
	}

	return resultList;
}