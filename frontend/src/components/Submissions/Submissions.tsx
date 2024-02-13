
import React, { useState } from 'react'
import { FetchMySubmission } from '../../api/upload';
import ResultCard from '../ResultCard/ResultCard';
import styles from "./Submisssion.module.scss";

type Submissionprops ={
  LicenseKey : string
}

const Submissions = ({LicenseKey} : Submissionprops) => {

  const [dataDocs, setdataDocs] = useState([])
  console.log(dataDocs);
  
  const fetchSubmisson = FetchMySubmission();
    React.useEffect(() => {
      

      fetchSubmisson.mutateAsync(LicenseKey ,{
        onSuccess: (data) => {
          console.log(data);
          setdataDocs(data.data?.docs)
  
          // const docsData = data?.data?.docs;
  
          // setSearchData(docsData);
          // setLoader(false);
          // setFirstSearch(false);
        },
      } )
    
      // return () => {
      //   second
      // }
    }, [])
    

  return (
    <div className={styles.results_container}>
    <h3>Your Submissions</h3>

    <div className={styles.results}>
      {dataDocs.length !== 0 && dataDocs.map((dataDoc, index) => {
        
        return <ResultCard key={index} data={dataDoc} />;
      
      })}
    </div>
  </div>
  )
}

export default Submissions