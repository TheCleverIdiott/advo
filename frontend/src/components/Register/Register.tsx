import React from "react";
import styles from "./register.module.scss";
import { InboxOutlined, UploadOutlined } from "@ant-design/icons";
import { Button, Checkbox, Form, Input, Upload } from "antd";
import { useRegisterUser } from "../../api/userService";
import { Navigate } from "react-router";

type registerProps = {
  state: any;
};

const Register = ({ state }: registerProps) => {
  const { isLoading, isSuccess, isError, error, handleRegister } =
    useRegisterUser();

    const token = localStorage.getItem("LicenseKey")

    if(token !== null){
      return <Navigate to="/search" />;
    }

  const onFinish = (values: any) => {
    console.log(values);

    handleRegister({
      ...values,
    });
  };

  const onFinishFailed = (errorInfo: any) => {
    console.log("Failed:", errorInfo);
  };

  const normFile = (e: any) => {
    console.log("Upload event:", e);
    if (Array.isArray(e)) {
      return e;
    }
    return e?.fileList;
  };

  return (
    <div className={styles.parentContainer}>
      <h1>Welcome to <span>nirnayaak</span></h1>
      <h3>Enter Your Credentials to Register</h3>

      <div className={styles.loginForm}>
        <Form
          name="basic"
          labelCol={{ span: 5 }}
          wrapperCol={{ span: 16 }}
          style={{
            width: "500px",
            marginLeft: "0",
            justifyContent: "flex-start",
          }}
          initialValues={{ remember: true }}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          autoComplete="off"
        >
          <Form.Item
            label="Name"
            name="name"
            labelAlign="left"
            rules={[{ required: true, message: "Please Enter your Name" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            label="Contact No"
            name="mobile"
            labelAlign="left"
            rules={[{ required: true, message: "Please Enter your Email" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            label="Designation"
            name="designation"
            labelAlign="left"
            rules={[
              { required: true, message: "Please Enter your Designation" },
            ]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="LicenseID"
            name="licenseID"
            labelAlign="left"
            rules={[
              { required: true, message: "Please Enter your Designation" },
            ]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            labelAlign="left"
            rules={[{ required: true, message: "Please input your password!" }]}
          >
            <Input.Password />
          </Form.Item>
          <Form.Item
            label="Upload ID"
            labelAlign="left"
            rules={[
              {
                required: true,
                message: "Please enter your designation proof",
              },
            ]}
          >
            <Form.Item
              name="dragger"
              valuePropName="fileList"
              getValueFromEvent={normFile}
            >
              <Upload.Dragger name="files" action="/upload.do">
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">
                  Click or drag file to this area to upload
                </p>
                <p className="ant-upload-hint">
                  Support for a single or bulk upload.
                </p>
              </Upload.Dragger>
            </Form.Item>
          </Form.Item>

          <Form.Item wrapperCol={{ offset: 0, span: 16 }}>
            <Button type="primary" htmlType="submit">
              Submit
            </Button>
          </Form.Item>
        </Form>
      </div>
      <p>
        Already have an account?{" "}
        <span
          onClick={() => {
            state("Login");
          }}
          style={{ color: "rgb(125, 189, 246)" }}
        >
          Login
          {/* need change state to login */}
        </span>
      </p>
    </div>
  );
};

export default Register;
