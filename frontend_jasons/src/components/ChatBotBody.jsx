import React, { useEffect } from "react";
import ChatIcon from "./ChatIcon";
import styles from "../styles/chatbody.module.css"
import ChatMessage from "./ChatMessage"
import { useRef } from "react";

function ChatBotBody({chatHistory}) 
{
   const bodyRef = useRef();
   useEffect(() =>{
      bodyRef.current.scrollTo({top: bodyRef.current.scrollHeight, behavior:"smooth"});
   },[chatHistory])
   return(
      <>
         <div ref={bodyRef} className={styles.chat_body}>
                  <div className={`${styles.message } ${styles.bot_message}`}>
                     <ChatIcon />
                     <p className={`${styles.message_text } ${styles.bot_message}`}>
                        How may i Assist you today?
                     </p>
                  </div>
                  {chatHistory.map((chat,index) =>
                     (<ChatMessage key={index} chat={chat}/>))}
                </div>
      </>
   )
}
export default ChatBotBody