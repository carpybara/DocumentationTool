import { applicationState } from "../../ApplicationModel/ApplicationState.model";

export function populateTimeoutList(data:applicationState['content']) :[] {
    const versionsDict = JSON.parse(JSON.stringify(data))['versions'];
    var listItems:any = [];

    for (let funcName in versionsDict) {
        if (funcName !== 'stats'){
            listItems.push({
                "funcName": String(funcName),
                "timeout": versionsDict[funcName]['stats']['timeout']
            })
        }
    }
    return listItems;
}