import styles from "../styles/chatbody.module.css"
import ChatIcon from "./ChatIcon";
const ChatMessage = ({chat}) =>
   {
      
      
            return(
               <div className={`${chat.role==="model" ? `${styles.message} ${styles.bot_message}` : `${styles.message} ${styles.user_message}`}
                  `}
                  >
                     {chat.role ==="model" && <ChatIcon />}
                     
                     <p className={`${chat.role==="model" ? `${styles.message_text} ${styles.bot_message}` : `${styles.message_text} ${styles.user_message}`}
                  `}>
                     {chat.text}
                     </p>
                  </div>
            );
        

     
   };
   export default ChatMessage;