import { applicationState } from "../../ApplicationModel/ApplicationState.model";
import { orderedTimes, inputType } from "./versioning.model";


export function populateVersionView(data:applicationState['content'], functionName:string) : orderedTimes[]{
	const versionsDict = JSON.parse(JSON.stringify(data))['versions'];
	if (!(functionName in versionsDict)){
		return [{
			version: '',
			timeRange: new Date(),
			value: 0
		}];
	}
	const functionDict = versionsDict[functionName];
	const callData = [] as inputType[];

	for (let version in functionDict) {
		if(version!=='stats') {
			//pop version stats object off, don't need here anyway.
			functionDict[version].pop();
			callData.push({
				"funcName": functionName,
				"timestamps": functionDict[version], 
				"version": version,
			});
			
		}
	}
	return getOrderedTimes(callData);
}

function getOrderedTimes(input: inputType[]): orderedTimes[]{
	//map timestamps to string, cut after hour, if timestamp not in outputList already, add entry to list, if it is, increase its counter ...
	var orderedTimes:orderedTimes[] = [];
	

	//iterate over versions
	for (let i = 0; i < input.length; i++){
		var timestampCountDict = {} as any; //reset dict so timeRange->count mapping is restarted for each version.
		//iterate over timestamps for current version

		for (let l = 0; l < input[i].timestamps.length; l++){
			let specificDate = new Date(input[i].timestamps[l] * 1000);
			let generalizedDate = specificDate.getFullYear() + '-' + specificDate.getMonth() + '-' + specificDate.getDate() + '\n' + specificDate.getHours() + ':00:00';
			
			//case: we have already seen a timestamp in this timerange.
			if (generalizedDate in timestampCountDict){
				timestampCountDict[generalizedDate] += 1;
			}
			//case: new timeRange found
			else {
				timestampCountDict[generalizedDate] = 1;
			}
	}
		for (let key in timestampCountDict){
			//var timeRange = new Date(key);
			orderedTimes.push({
				version: 'v' + input[i]['version'],
				timeRange: key,
				value: timestampCountDict[key]
			});
		}
	}
	//Have to order so the plotting is correct.
	orderedTimes.sort((a, b) => (a.timeRange > b.timeRange) ? 1 : -1)

	return orderedTimes;
}

export function getInfoPerVersion(data:applicationState['content'], functionName:string) {
	const functionDict = JSON.parse(JSON.stringify(data))['versions'][functionName];
	const versionInfoDict = {} as any;

	for(let key in functionDict){
		if(key !== "stats"){
			let versionLength = functionDict[key].length
			var computation = functionDict[key][versionLength-1]['total_computation']
			versionInfoDict[key] = computation;
		}
	}
	return versionInfoDict;
}