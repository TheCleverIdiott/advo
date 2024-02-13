import React from "react";
import { InboxOutlined, UploadOutlined } from "@ant-design/icons";
import {
  Button,
  Checkbox,
  Form,
  Input,
  message,
  Upload,
  UploadProps,
} from "antd";

import styles from "./UploadPDF.module.scss";
import Dragger from "antd/es/upload/Dragger";
import { FetchMySubmission, FetchSearchQuery } from "../../api/upload";

const submitType = {
  upload: "upload",
  preprocess: "preprocess",
};

const UploadPDF = () => {
  const [documentState, setDocumentState] = React.useState(submitType.upload);
  const [preProcessLoading, setPreProcessLoading] = React.useState(false);

  const [documentId, setdocumentId] = React.useState("");

  const preprocessquery = FetchSearchQuery();
  const licenseID = localStorage.getItem("LicenseKey")
  const fetchSubmisson = FetchMySubmission();

  const onFinish = (values: any) => {
    console.log("Success:", values);
  };

  const preProcess = () => {
    preprocessquery.mutateAsync(documentId, {
      onSuccess(response) {
        message.success(`file Processed successfully.`);
        window.location.reload();
      },
      onError(response) {
        message.error(`Failed processing file.`);
      },
    });
  };

  // const onFinishFailed = (errorInfo: any) => {
  //   message.error(`Enter Required Credentials`);
  // };

  // const normFile = (e: any) => {
  //   console.log("Upload event:", e);
  //   if (Array.isArray(e)) {
  //     return e;
  //   }
  //   return e?.fileList;
  // };

  const props: UploadProps = {
    name: "user_file",
    multiple: true,
    action: `https://ml-backend.nirnayaak.co/upload?licenseID=${licenseID}`,
    onChange(info) {
      console.log(info);

      const { status, response } = info.file;
      if (status !== "uploading") {
        console.log(response);
        setdocumentId(response?.documentID);
      }
      if (status === "done") {
        message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === "error") {
        message.error(`${info.file.name} file upload failed.`);
      }
    },

    // onSuccess(res: any, file: any) {
    //   console.log("onSuccess", res, file.name);

    // },
    onDrop(e) {
      console.log("Dropped files", e.dataTransfer.files);
    },
  };

  return (
    <div className={styles.parentContainer}>
      <h3>Upload Document</h3>
      <Dragger style={{height: "400px"}} {...props}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">
          Click or drag file to this area to upload
        </p>
        <p className="ant-upload-hint">Support for a single or bulk upload</p>
      </Dragger>
      <Button
        block
        type="primary"
        loading={preprocessquery.isLoading}
        style={{
          width: "300px",
          margin: "1rem 0rem",
          backgroundColor:
            documentState === submitType.preprocess ? "green" : "",
          color: documentState === submitType.preprocess ? "white" : "",
        }}
        disabled={documentId !== "" ? false : true}
        onClick={() => {
          preProcess();
        }}
      >
        {preprocessquery.isLoading ? "Lawyering Up" : "Process My Document"}
      </Button>
    </div>
  );
};

export default UploadPDF;
