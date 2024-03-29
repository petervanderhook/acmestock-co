import logo from './logo.png';
import './App.css';

import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'
import HealthStats from './components/HealthStats'

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
                    <h3>Stock Status</h3>
                    <AppStats/>
            
                </div>
            </div>
            <h1>Audit Endpoints</h1>
            {rendered_endpoints}
            <p className="gapper"></p>
            <div className='stats'>
                <div className='statscontainer'>
                    <h3>Health Stats</h3>
                    <HealthStats/>
            
                </div>
            </div>
        </div>
    );

}



export default App;
