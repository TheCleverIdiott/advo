import React from 'react';
import { Space, Spin } from 'antd';
import  './loader.css';

const App: React.FC = () => (
  // <Space size="middle">
  //   <Spin size="small" />       
  // </Space>
  <div className='parent'>
  <div className="typewriter">
    <div className="slide"><i></i></div>
    <div className="paper"></div>
    <div className="keyboard"></div>
  </div>
  </div>
);

export default App