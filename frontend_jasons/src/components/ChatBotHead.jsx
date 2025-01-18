import React from "react";
import styles from "../styles/chatbothead.module.css"
import ChatIcon from "./ChatIcon";
function ChatBotHead({setShowChatbot}) 
{
   return(
      <>
         <div className={styles.chat_header}>
                  <div className={styles.header_info}>
                     <ChatIcon />
                     <h2>SunireChatBot</h2> 
                  </div>
                  <button onClick={() =>setShowChatbot(prev => !prev)} className="material-symbols-rounded">
                           Keyboard_arrow_down 
                     </button>
               </div>
      </>
   )
}
export default ChatBotHead
