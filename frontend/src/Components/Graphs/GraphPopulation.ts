import { version } from "os";
import { BarData } from "../../ApplicationModel/ApplicationState.model";
import { findLargestNumber } from "./GraphLogic";

export function populateOptimizationView(data:string) :ReadonlyArray<BarData> {
	
	const versioningDict = JSON.parse(JSON.stringify(data))['versions'];
	const optimizationDict = [] as any;
	const amtOfFunctions = Object.keys(versioningDict).length-1;

	for (let key in versioningDict){
		if (key!=='stats'){
			let versions = Object.keys(versioningDict[key]).filter(item => item!=="stats");
			let latestVersion = findLargestNumber(versions);

			let lastElementPlace:number = versioningDict[key][latestVersion].length-1;
			let stats:any = versioningDict[key][String(latestVersion)][lastElementPlace]
			let configuredMem:number = versioningDict[key]['stats']['memorySize']
			optimizationDict.push({
				FunctionName: amtOfFunctions <= 8 ? (key.slice(0, 25) + '\n' + key.slice(25, 50)) : (key.slice(0, 10) + '\n' + key.slice(10, 20) + '\n' + key.slice(20, 30) + '\n' + key.slice(30, 40) + '\n' + key.slice(40, 50)),
				StatType: 'Remaining Memory',
				Value: Math.round((configuredMem - stats['version_avg_maxMemoryUsed'])/10000)/100
			});

			optimizationDict.push({
				FunctionName: amtOfFunctions <= 8 ? (key.slice(0, 25) + '\n' + key.slice(25, 50)) : (key.slice(0, 10) + '\n' + key.slice(10, 20) + '\n' + key.slice(20, 30) + '\n' + key.slice(30, 40) + '\n' + key.slice(40, 50)),
				StatType: 'Used Memory',
				Value: (Math.round(stats['version_avg_maxMemoryUsed']/10000)/100)
			});

		}
	}
	return optimizationDict;
}


export function populateTotalLambdaCosts(data:string) :Object[] {
	const versioningDict = JSON.parse(JSON.stringify(data))['versions'];
	const listData = [];
	const listDict = {} as any;
	let totalComputation:number = +versioningDict['stats']['app_computation'];

	for (let func_name in versioningDict){
		if (func_name!=='stats'){
			let computation:number = Math.round(versioningDict[func_name]['stats']['func_total_computation']*1000)/1000;

			let percentage:number = (computation / totalComputation) * 100;
			listDict[percentage] = [func_name, computation];
		}
	}

	let sortedPercentages:any = Object.keys(listDict).sort((a, b) => parseFloat(b) - parseFloat(a));
	var enumerator = 1;
	for (let key in sortedPercentages){
		let respectiveFunction = listDict[sortedPercentages[key]];
		listData.push(
			{
				functionName: respectiveFunction[0],
				value: respectiveFunction[1]
			}
		);
		enumerator += 1;
	}
	return listData;
}

