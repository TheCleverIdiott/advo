import React from "react";
import { Tabs } from "antd";
import type { TabsProps } from "antd";
import styles from "./User.module.scss";
import UploadPDF from "../../components/UploadPDF/UploadPDF";
import Submissions from "../../components/Submissions/Submissions";
import { Navigate, redirect, useNavigate } from "react-router";
import { FetchMySubmission } from "../../api/upload";
import { Link } from "react-router-dom";

const onChange = (key: string) => {
  console.log(key);
};

// const items: TabsProps["items"] = [
//   {
//     key: "1",
//     label: `Upload PDF`,
//     children: <UploadPDF></UploadPDF>,
//   },
//   {
//     key: "2",
//     label: `View Submissions`,
//     children: <Submissions />,
//   },
// ];

const User = () => {
  const localStorageLicenseKey = localStorage.getItem("LicenseKey");
  console.log(localStorageLicenseKey);

  const navigate = useNavigate();

  if (localStorageLicenseKey === null) {
    return <Navigate to="/authentication" />;
  }

  return (
    <div className={styles.parentContainer}>
      <div className={styles.top}>
        <img
          style={{ width: "30px", marginRight: "2rem" }}
          src={process.env.PUBLIC_URL + "/images/Logo.png"}
        />
        <div className={styles.navButtons}>
          <Link className={styles.navButtonsLinks} to={"/search"}>
            Search Tags
          </Link>
          <Link className={styles.navButtonsLinks} to={"/judgementsearch"}>
            Suggest Actions
          </Link>
        </div>
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
      </div>
      <div className={styles.bottom}>
        <UploadPDF></UploadPDF>
        <Submissions LicenseKey={localStorageLicenseKey} />
      </div>
      {/* <Tabs style={{height: "100%"}} defaultActiveKey="1" items={items} onChange={onChange} /> */}
    </div>
  );
};

export default User;
