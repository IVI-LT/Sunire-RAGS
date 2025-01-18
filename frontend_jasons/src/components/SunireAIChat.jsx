import React, { useState } from "react";
import ChatBotHead from "./ChatBotHead";
import ChatBotBody from "./ChatBotBody";
import ChatBotFooter from "./ChatbotFooter";
import styles from "../styles/SunireAIChat.module.css"

function SunireAIChat() 
{
   const [chatHistory,setChatHistory] = useState([])
   const [showChatbot,setShowChatbot] = useState(false)
   const [isAnimating, setIsAnimating] = useState(false);
   const HTTP= "http://localhost:9020/chat";

   const toggleChatbot = () => {
      if (showChatbot) {
         // Start hiding animation
         setIsAnimating(true);
         setTimeout(() => {
           setShowChatbot(false);
           setIsAnimating(false);
         }, 300); // Match CSS transition duration (0.3s)
       } else {
         setShowChatbot(true);
       }
    };
   const getModelResponse = async (history) =>
   {console.log(history);
      history = history.map(({role,text}) =>({role,content:{text}}));

      const user_messages = history.filter(msg => msg.role !== "model");
      console.log(user_messages);
      const mostrecentchat = history[history.length - 1];
      const user_prompt = mostrecentchat["content"]["text"];   
      
      const requestSever ={
         method: "POST",
         headers: {
            'Content-type': 'application/json; charset=UTF-8',
         },
         body: JSON.stringify({
            prompt:{user_prompt}
         })
      }
      try{
         let response = await fetch(HTTP, requestSever);
         if(!response.ok) throw new Error(data.error.message || "An Error has Occur")
         // Handle the response as a stream
         const reader = response.body.getReader();
         const decoder = new TextDecoder("utf-8");
         let result = "";
         while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            // Decode and append the streamed data
            result += decoder.decode(value, { stream: true });

            // Optional: Update chat history in real-time
            setChatHistory((prev) => [
                ...prev.filter(msg => msg.text !== "Thinking.."),
                { role: "model", text: result.trim() }
            ]);
        }
        
            console.log("Final result:",result);
      }catch(error)
      {
         console.log(error);
      }
      
   }
   
   return(
      <>
      <div className={styles.container} >
         <div className={styles.chat_container}>
         {showChatbot && (
            <div className={`${!isAnimating ? styles.chatbot_popup : styles.showpop_up}`} >
             
            {/* Chatbot Header*/}
            <ChatBotHead setShowChatbot={setShowChatbot}/>
             {/* Chatbot Body*/}
             <ChatBotBody chatHistory={chatHistory}/>
             {/* Chatbot footer*/}
             <ChatBotFooter setChatHistory={setChatHistory} getModelResponse={getModelResponse} chatHistory={chatHistory}/>
                </div>)}
            
            
            <button onClick={toggleChatbot} id={`${showChatbot ?  styles.mini : ""}`} className={styles.chat_toggler}>
                  <span 
                  className="material-symbols-rounded">
                  { showChatbot ?  "close" : "mode_comment"}
               </span >
               
            </button>
         </div>
      </div>
         
      </>
      
   )
}
export default SunireAIChat