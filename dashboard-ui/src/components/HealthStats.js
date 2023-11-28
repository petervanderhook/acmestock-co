import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://stinky.westus3.cloudapp.azure.com:80/health/get_stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div class='latest-stats-div'>
                <table className={"StatsTable"}>
					<tbody>
                        <h1>Health Status</h1>
						<tr>
							<td><h5><b>Storage Service:</b></h5></td>
                            <td>{stats['storage']}</td>
                        </tr>
                        <tr>
							<td><h5><b>Audit Service:</b></h5></td> 
                            <td>{stats['audit']}</td>
						</tr>
                        <tr>
							<td><h5><b>Processing Service</b></h5></td> 
                            <td>{stats['processing']}</td>
						</tr>
                        <tr>
							<td><h5><b>Receiver Service:</b></h5></td> 
                            <td>{stats['receiver']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>
            </div>
        )
    }
}
