import { applicationState } from "../../ApplicationModel/ApplicationState.model";

export function getStartupData(data:string) :any{
    const versionsDict = JSON.parse(JSON.stringify(data))['versions'];
    const outputDict:any = {};

    for (let funcName in versionsDict){
        if(funcName!=='stats'){
            let initDuration = versionsDict[funcName]['stats']['current_avg_initDuration'];
            outputDict[funcName] = {
                'current_avg_initDuration': initDuration,
                'layers': []
            }
            let layerList = versionsDict[funcName]['stats']['layerList'];
            for (let i=0; i < layerList.length; i++){
                var codeSize = +layerList[i].CodeSize / 1000000; //in MB
                var arn = layerList[i].Arn;
                outputDict[funcName]['layers'].push({
                    'name': arn.slice(arn.indexOf(':layer:')+7),
                    'size': Math.round(codeSize * 100)/100
                });
            }
        }
    }
    return outputDict;
}