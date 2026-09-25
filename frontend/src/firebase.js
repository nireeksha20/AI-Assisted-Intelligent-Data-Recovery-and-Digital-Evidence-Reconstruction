import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDs1xvaOJTykYQ_kZcJiWSIU70gRsLM5Ew",
  authDomain: "reclaimai-project.firebaseapp.com",
  projectId: "reclaimai-project",
  storageBucket: "reclaimai-project.firebasestorage.app",
  messagingSenderId: "237817355454",
  appId: "1:237817355454:web:3dd4ddeaf002b6c56e92ef",
  measurementId: "G-DJVEME2C8V"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);

export const googleProvider = new GoogleAuthProvider();