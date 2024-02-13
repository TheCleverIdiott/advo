import React from "react";
import styles from "./Login.module.scss";
import { Button, Checkbox, Form, Input, message } from "antd";
import { useLoginQuery } from "../../api/userService";
import { Navigate } from "react-router";

type loginprops = {
  state: any;
};

const Login = ({ state }: loginprops) => {
  const loginUser = useLoginQuery();

  const token = localStorage.getItem("LicenseKey");

  if (token !== null) {
    return <Navigate to="/search" />;
  }

  const onFinish = (values: any) => {
    loginUser.mutateAsync(
      {
        ...values,
      },
      {
        onSuccess(res) {
          message.success("Sucessfully Logged in");
        },
        onError(res) {
          console.log(res);

          message.error("Use Valid Credentials");
        },
      }
    );
  };

  const onFinishFailed = (errorInfo: any) => {
    console.log("Failed:", errorInfo);
  };

  return (
    <div className={styles.parentContainer}>
      <h1>Welcome to <span>nirnayaak</span></h1>
      <h3>Login into your account by entering your credentials</h3>

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
            label="Contact No"
            name="mobile"
            labelAlign="left"
            rules={[{ required: true, message: "Please Enter your Email" }]}
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

          <Form.Item wrapperCol={{ offset: 0, span: 16 }}>
            <Button type="primary" htmlType="submit">
              Submit
            </Button>
          </Form.Item>
        </Form>
      </div>
      <p>
        don't have an account?{" "}
        <span
          onClick={() => {
            state("Register");
          }}
          style={{ color: "rgb(125, 189, 246)" }}
        >
          Register Here
        </span>
      </p>
    </div>
  );
};

export default Login;
