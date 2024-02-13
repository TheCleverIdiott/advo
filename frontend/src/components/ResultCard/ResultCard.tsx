import React from "react";
import { redirect, useNavigate } from "react-router";
import { Link } from "react-router-dom";
import styles from "./ResultCard.module.scss";
import { BsFillFilePdfFill } from "react-icons/bs";
import { BiInfoCircle } from "react-icons/bi";


type resultCardProps = {
  data: any;
};

const ResultCard = (props: resultCardProps) => {
 
  
  console.log("props data" , props);
  
  const Navigate = useNavigate();

  return (
    <div className={styles.resultCardContainer}>
      <div className={styles.heading}>{props.data?.title}</div>
      <div className={styles.resultMetaData}>
        <p>{props.data?.date}</p>
        <p>{props.data?.court}</p>
      </div>
      <div className={styles.summary}>
        {props.data?.summary.substring(0, 400)}...
      </div>
      <div className={styles.relatedTags}>
        <div className={styles.tagHeading}>Related Tags:</div>

        {props.data?.keywords?.length >= 7 ? (
          <div className={styles.tags}>
            <span>{props.data?.keywords[0]}</span>
            <span>{props.data?.keywords[1]}</span>
            <span>{props.data?.keywords[2]}</span>
            <span>{props.data?.keywords[3]}</span>
            <span>{props.data?.keywords[4]}</span>
            <span>{props.data?.keywords[5]}</span>
            <span>{props.data?.keywords[6]}</span>
          </div>
        ) : (
          <div className={styles.tags}>
            {props.data?.keywords.map((keyword: string, index: number) => {
              <span key={index}>{keyword}</span>;
            })}
          </div>
        )}
      </div>
      <div className={styles.buttons}>
        <button
        style={{
          marginRight : "1rem"
        }}
          onClick={() => {
            Navigate(`/document/${props.data._id}`);
          }}
          className={styles.button}
        >
          {" "}
          <BiInfoCircle style={{fontSize: "1rem" , marginRight: "0.5rem"}} />
          More Information
        </button>
        <Link className={styles.link} to={props.data.documents[0].url} target="_blank">
        <button
          // onClick={() => {
          //   console.log(props.data.documents[0].url);
            
          //   redirect(props.data.documents[0].url)
          // }}
          className={styles.button}
        >
          <BsFillFilePdfFill style={{fontSize: "1rem" , marginRight: "0.5rem"}} />
          Show PDF
        </button>
        </Link>
        
      </div>
    </div>
  );
};

export default ResultCard;
