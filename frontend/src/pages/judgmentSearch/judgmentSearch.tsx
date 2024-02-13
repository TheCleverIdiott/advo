import React from "react";
import { AudioOutlined } from "@ant-design/icons";
import { Input, Space } from "antd";
import styles from "./judgmentsearch.module.scss";
import { FetchSearchQuery2 } from "../../api/Search";
import Loader from "../../components/Loader/Loader";
import ResultCard from "../../components/ResultCard/ResultCard";
import { Link, useNavigate } from "react-router-dom";

const { Search } = Input;

const suffix = (
  <AudioOutlined
    style={{
      fontSize: 16,
      color: "#1890ff",
    }}
  />
);

const JudgementSearch = () => {
  const [loading, setLoading] = React.useState(false);
  const [gptText, setGptText] = React.useState("");
  const [searchData, setSearchData] = React.useState([]);
  const [dataFetch, setDataFetch] = React.useState(false);
  const fetchResult = FetchSearchQuery2();

  const licenseID = localStorage.getItem("LicenseKey")
  const navigate = useNavigate()

  const onSearch = (value: string) => {
    setLoading(true);
    fetchResult.mutateAsync(value, {
      onSuccess: (data) => {
        console.log(data?.data);

        const docsData = data?.data?.docs;
        setGptText(data?.data?.gpt_res);
        setSearchData(docsData);
        setDataFetch(true);
        setLoading(false);
      },
    });
    //setLoading(false);
  };

  return (
    <>
      <div className={styles.judge_cont}>
      <div className={styles.top}>
      <img
              style={{ width: "30px", marginRight: "2rem" }}
              src={process.env.PUBLIC_URL + "/images/Logo.png"}
            />
        <div className={styles.navButtons}>
          <Link className={styles.navButtonsLinks} to={"/user"}>
            Upload
          </Link>
          <Link className={styles.navButtonsLinks} to={"/search"}>
            Search Tags
          </Link>
        </div>

        {licenseID !== null && (
          <div className={styles.top_left}>
            <button
              onClick={() => {
                localStorage.removeItem("LicenseKey");
                navigate("/authentication");
              }}
            >
              Logout
            </button>
            <img
              style={{ width: "40px", marginRight: "2rem" }}
              src={process.env.PUBLIC_URL + "/images/avataaars.png"}
            />
          </div>
        )}
      </div>
        <h1>nirnayaak</h1>
        <h3>Suggestion Portal</h3>
        <div className={styles.search}>
          <Search
            className="search"
            placeholder="Enter your query..."
            enterButton="Search"
            size="large"
            suffix={suffix}
            onSearch={onSearch}
            loading={loading}
          />
        </div>
        {loading ? (
          <Loader  />
        ) : dataFetch ? (
          <div className={styles.gpt_response}>
            <h4>Our Suggestion For You:</h4>
            <p>{gptText}</p>
          </div>
        ) : null}
        {dataFetch ? (
          searchData.length === 0 ? (
            <div className={styles.results_container}>
              No related content found
            </div>
          ) : (
            <div className={styles.results_container}>
              <h3>Similar documents we found just for you</h3>

              <div className={styles.results}>
                {searchData.map((data, index) => {
                  return <ResultCard key={index} data={data} />;
                })}
              </div>
            </div>
          )
        ) : null}
      </div>
    </>
  );
};

export default JudgementSearch;
