import { Menu } from 'antd';

import { useState } from 'react';
import { applicationState } from '../../ApplicationModel/ApplicationState.model';
import Page1 from '../Sites/Page1';
import Page2 from '../Sites/Page2';
import Page3 from '../Sites/Page3';




export const NavBar = (props:
    {state: applicationState}
  ) => {
  const [selected, setMenuItem]= useState(['item1']);
 
  const pageSwitcher = (key:string[]) => {
  const flat = key[0]
  switch (flat) {
    case 'item1':
      return Page1(props.state)
    case 'item2':
      return Page2(props.state)
    case 'item3':
      return Page3(props.state)
    default:
      console.log(key)
      return (<h3>broken</h3>);

   }
  }
 
 return(
  <div>
   <Menu selectedKeys={selected} mode="horizontal" onClick={e => 
         setMenuItem([e.key])}>
     <Menu.Item key="item1">Overview</Menu.Item>
     <Menu.Item key="item2">Optimization</Menu.Item>
     <Menu.Item key="item3">Configuration</Menu.Item>
    </Menu>
    <div>
      {pageSwitcher(selected)}
    </div>
  </div>)

}
