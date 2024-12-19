/*

import React , {useState} from 'react';
import axios from 'axios';

export default function SunireGPT() {
    
    const [prompt, setPrompt] = useState("");
    const [response, setResponse] = useState("");
    const HTTP= "http://localhost:8020/chat";
    const handleSubmit = (e) => {
        e.preventDefault();
        axios
            .post(`${HTTP}`, {prompt})
            .then((res) => {
                setResponse(res.data);
                console.log(prompt);
                console.log("Response:", res.data);
            })
            .catch((error) => {
                console.log(error);
            });

        setPrompt("");
    };
    const handlePrompt = (e) => setPrompt(e.target.value);
    /*return ( 
    <div className = "container container-sm p-1">
        <h1 className="title text-center text-darkGreen">LLM</h1>
        <from className="form" onSubmit={handleSubmit}>
            <div className='form' onSubmit={handleSubmit}>
                <label htmlFor="">Ask questions</label>
                <input type="text" 
                className="shadow-sm" 
                placeholder="Enter text" 
                value={prompt}
                onChange={handlePrompt}
                />
            </div>
        </from>
        <div className="bg-darkGreen mt-2 p-1 border-5">
            <p className="text-light">
                {response ? response : "Skin Cancer related awns..."}
            </p>
        </div>
    </div>);
    */
/*
    return (
      <div className="container container-sm p-1">
        {" "}
        <h1 className="title text-center text-darkGreen">ChatGPT API</h1>
        <form className="form" onSubmit={handleSubmit}>
          <div className="form-group">
            <a href="">Link</a>
            <label htmlFor="">Ask questions</label>
            <input
              className="shadow-sm"
              type="text"
              placeholder="Enter text"
              value={prompt}
              onChange={handlePrompt}
            />
          </div>{" "}
          {/* <button className="btn btn-accept w-100" type="submit">
            Go
          </button> *//*}
        </form>
        <div className="bg-darkGreen  mt-2 p-1 border-5">
          <p className="text-light">
            {response ? response : "Skin cancer related awns go here..."}
          </p>
        </div>
      </div>
    );
}

*/

import React , {useState} from 'react';
import axios from 'axios';

export default function SunireGPT() {

    const [prompt, setPrompt] = useState("");
    const [response, setResponse] = useState("");
    const HTTP= "http://localhost:9020/chat";
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        /* axios
            .post(`${HTTP}`, {prompt}, { responseType: 'stream' })
            .then(
              (res) => {
                setResponse(res.data);
                console.log(prompt);
                console.log("Response:", res.data);
            })
            .catch((error) => {
                console.log(error);
            });*/

          //store response
          setResponse("")
            try {
              const res = await fetch(HTTP, {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json'
                  },
                  body: JSON.stringify({ prompt })
              });
  
              const reader = res.body.getReader();
              const decoder = new TextDecoder('utf-8');
  
              function read() {
                  reader.read().then(({ done, value }) => {
                      if (done) {
                          return;
                      }
                      const chunk = decoder.decode(value, { stream: true });
                      setResponse((prev) => prev + chunk);
                      read();
                  });
              }
  
              read();
          } catch (error) {
              console.error("Error:", error);
          }
        setPrompt("");
    };
    const handlePrompt = (e) => setPrompt(e.target.value);
    /*return ( 
    <div className = "container container-sm p-1">
        <h1 className="title text-center text-darkGreen">LLM</h1>
        <from className="form" onSubmit={handleSubmit}>
            <div className='form' onSubmit={handleSubmit}>
                <label htmlFor="">Ask questions</label>
                <input type="text" 
                className="shadow-sm" 
                placeholder="Enter text" 
                value={prompt}
                onChange={handlePrompt}
                />
            </div>
        </from>
        <div className="bg-darkGreen mt-2 p-1 border-5">
            <p className="text-light">
                {response ? response : "Skin Cancer related awns..."}
            </p>
        </div>
    </div>);*/

    return (
        <div className="container container-sm p-1">
          {" "}
          <h1 className="title text-center text-darkGreen">ChatGPT API</h1>
          <form className="form" onSubmit={handleSubmit}>
            <div className="form-group">
              <a href="">Link</a>
              <label htmlFor="">Ask questions</label>
              <input
                className="shadow-sm"
                type="text"
                placeholder="Enter text"
                value={prompt}
                onChange={handlePrompt}
              />
            </div>{" "}
            {<button className="btn btn-accept w-100" type="submit">
              Submit
            </button>}
          </form>
          <div className="bg-darkGreen  mt-2 p-1 border-5">
            <p className="text-light">
              {response ? response : "Skin cancer related awns go here..."}
            </p>
          </div>
        </div>
      );
    
}