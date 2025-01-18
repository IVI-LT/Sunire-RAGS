import React from "react";
import styles from "../styles/chatfooter.module.css"
import { useRef } from "react";
function ChatBotFooter({setChatHistory , getModelResponse, chatHistory}) 
{
   const inputRef = useRef()
   const handleFromSumnit =(e) =>
   {
      e.preventDefault();
      const userMessage = inputRef.current.value.trim();
      if(!userMessage) return;
      inputRef.current.value ="";
      setChatHistory((history) =>[...history, {role:"user", text:userMessage }]);
     setTimeout(() => {
      setChatHistory((history) =>[...history, {role:"model", text:"Thinking.." }]);
      getModelResponse([...chatHistory, {role:"user", text:userMessage }]);
   },600) 
   }
   return(
      <>
         <div className={styles.chat_footer}>
            <form action="#"  
            onSubmit={handleFromSumnit} 
            className={styles.chat_form}>
               <input ref={inputRef} 
               type="text" 
               placeholder="Question?"  
               className={styles.chat_input} 
               required />
            <button 
            className="material-symbols-rounded">
            arrow_right
            </button>
            </form>
         </div>
      </>
   )
}
export default ChatBotFooter