import { useState } from "react";
import api from "../services/api";

export default function Login() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const login = async () => {

        try {

            const response = await api.post("/auth/login", {
                email,
                password
            });

            localStorage.setItem(
                "token",
                response.data.access_token
            );

            alert("Login Successful!");

        } catch (err) {
            alert("Invalid Credentials");
        }

    };

    return (

        <div style={{padding:"40px"}}>

            <h1>AI Code Reviewer</h1>

            <input
                placeholder="Email"
                value={email}
                onChange={(e)=>setEmail(e.target.value)}
            />

            <br/><br/>

            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e)=>setPassword(e.target.value)}
            />

            <br/><br/>

            <button onClick={login}>
                Login
            </button>

        </div>

    );

}