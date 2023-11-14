import logo from './logo.png';
import './App.css';

import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'

function App() {

    const endpoints = ["get_stock_quantity", "get_stock_price"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })

    return (
        <div className="App">
            <div className="logo-container">
                <img src={logo} className="App-logo" alt="logo" height="150px" width="400px"/>
            </div>
            <h1>Latest Stats</h1>
            <div className='stats'>
                <div className='statscontainer'>
                    <AppStats/>
            
                </div>
            </div>
            <h1>Audit Endpoints</h1>
            {rendered_endpoints}
            <p className="gapper"></p>
        </div>
    );

}



export default App;
