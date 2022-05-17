import { Radio, Space } from "antd"
import Title from "antd/lib/typography/Title";
import { applicationState, requestArgs } from "../../ApplicationModel/ApplicationState.model"


function formatDeploymentName(fileName:string) :string{
  if(!(fileName.includes('ArchitectureState'))){
    return fileName;
  }
  const shortened:string = fileName.split('/')[1].split('.')[0];
  const date:string = shortened.split('_')[2];
  const dateString = date.substring(0, 4) + '-' + date.substring(4,6) +'-'+ date.substring(6,11) +':'+ date.substring(11,13) +':'+ date.substring(13,15) + 'Z';
  const date_date = new Date(dateString)
  const finalString = "Application State until " + checkDoubleDigit(String(date_date.getDate()))+"-"+checkDoubleDigit(String(date_date.getMonth()+1))+"-"+String(date_date.getFullYear())+" "+checkDoubleDigit(String(date_date.getHours()))+":"+checkDoubleDigit(String(date_date.getMinutes()))+":"+checkDoubleDigit(String(date_date.getSeconds()));
  return finalString;
}

function checkDoubleDigit(input:string):string {
  if (input.length===1){
    return '0'+input;
  }
  return input
}


export const DeploymentOptions = (props:{
  state: applicationState
  onclickEvent: any
})=>{
  if(props.state.availableDeploymentDocumentation.length===0){
    return <>
    <Title level={3}>No deployments detected.</Title>
    </>
  }

  return <>
    <Radio.Group defaultValue="a" size="large">
      <Space direction="vertical">
      {props.state.availableDeploymentDocumentation.map(d => {
        return <Radio.Button value={d} onClick={()=>props.onclickEvent({arg1: 'fetch', arg2:d, arg3:true} as requestArgs)}>{formatDeploymentName(d)}</Radio.Button>
        })}
</Space>
</Radio.Group></>
}

