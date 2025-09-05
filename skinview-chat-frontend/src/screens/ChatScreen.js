import React, { useState, useEffect, useRef } from "react";
import {
    Platform,
    KeyboardAvoidingView,
    TextInput,
    TouchableOpacity,
    ScrollView,
    View,
    Text,
    StyleSheet,
    Keyboard,
    Image,
    Alert
} from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import apiClient from '../api/client';
import ChatBotMessage from '../components/ChatBotMessage';
import UserMessage from "../components/UserMessage";

const ChatScreen = ({ route, navigation }) => {
    // --- 상태 관리 (State) ---
    const [messages, setMessages] = useState(route.params?.initialMessages || []);
    const [inputText, setInputText] = useState("");
    const [userKey, setUserKey] = useState("seungjae_key");
    const [animatingMessage, setAnimatingMessage] = useState(null);
    const [isAtBottom, setIsAtBottom] = useState(true);
    const scrollViewRef = useRef();

    // --- 생명주기 및 효과 (Hooks) ---
    useEffect(() => {
        if (!animatingMessage) return;

        const { id, fullText } = animatingMessage;
        let index = 0;
        const intervalId = setInterval(() => {
            if (index < fullText.length) {
                setMessages(prev => prev.map(msg => msg.id === id ? { ...msg, text: fullText.substring(0, index + 1) } : msg));
                index++;
            } else {
                clearInterval(intervalId);
                setAnimatingMessage(null);
            }
        }, 30);

        return () => clearInterval(intervalId);
    }, [animatingMessage]);

    useEffect(() => {
        const keyboardDidShowListener = Keyboard.addListener('keyboardDidShow', () => {
            setTimeout(() => {
                if (scrollViewRef.current) {
                    scrollViewRef.current.scrollToEnd({ animated: true });
                }
            }, 100);
        });
        return () => keyboardDidShowListener.remove();
    }, []);

    // --- 핸들러 함수 (Event Handlers) ---
    const handleResetChat = async () => {
        Alert.alert(
            "대화 초기화",
            "대화 기록을 정말 초기화하시겠습니까?",
            [
                { text: "취소", style: "cancel" },
                {
                    text: "확인",
                    onPress: async () => {
                        try {
                            const response = await apiClient.post("/reset", { user_key: userKey });
                            const newQuickReplies = response.data?.quick_replies || [];

                            const initialMessage = {
                                id: "bot-welcome-reset",
                                type: "bot",
                                text: "무엇을 도와드릴까요?",
                                time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                                quickReplies: newQuickReplies
                            };

                            setMessages([initialMessage]);
                            scrollViewRef.current?.scrollTo({ y: 0, animated: true });

                        } catch (error) {
                            console.error("대화 기록 초기화 실패:", error);
                            Alert.alert("오류", "대화 기록 초기화에 실패했습니다. 다시 시도해주세요.");
                        }
                    },
                    style: "destructive"
                }
            ]
        );
    };

    const sendMessage = async (text) => {
        if (!text.trim() || animatingMessage) return;

        const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        const userMessage = { id: `user-${Date.now()}`, type: "user", text, time };

        setMessages(prev => {
            const newMessages = [...prev];
            const lastMessageIndex = newMessages.length - 1;
            if (lastMessageIndex >= 0 && newMessages[lastMessageIndex].type === 'bot' && newMessages[lastMessageIndex].quickReplies) {
                const updatedLastMessage = { ...newMessages[lastMessageIndex] };
                delete updatedLastMessage.quickReplies;
                newMessages[lastMessageIndex] = updatedLastMessage;
            }
            return [...newMessages, userMessage];
        });

        setInputText("");
        const botMessagePlaceholder = { id: `bot-${Date.now()}`, type: "bot", text: "...", time };
        setMessages(prev => [...prev, botMessagePlaceholder]);

        try {
            const response = await apiClient.post("/message", { user_key: userKey, message: text });
            const botReply = response.data?.reply;
            const quickReplies = response.data?.quick_replies;

            if (botReply) {
                const newBotMessage = {
                    ...botMessagePlaceholder,
                    text: "", // 타이핑 애니메이션을 위해 비움
                    quickReplies: quickReplies || []
                };
                setMessages(prev => prev.map(msg => msg.id === botMessagePlaceholder.id ? newBotMessage : msg));
                setAnimatingMessage({ id: botMessagePlaceholder.id, fullText: botReply });
            } else {
                setMessages(prev => prev.filter(msg => msg.id !== botMessagePlaceholder.id));
                Alert.alert("오류", "서버에서 응답이 없습니다.");
            }
        } catch (error) {
            console.error("메시지 전송 오류:", error);
            setMessages(prev => prev.map(msg => msg.id === botMessagePlaceholder.id ? { ...msg, text: "서버 통신 중 오류가 발생했습니다." } : msg));
        }
    };

    const handleQuickReplyPress = (text) => {
        sendMessage(text);
    };

    const handleScroll = (event) => {
        const { layoutMeasurement, contentOffset, contentSize } = event.nativeEvent;
        const paddingToBottom = 20;
        const isScrolledToBottom = layoutMeasurement.height + contentOffset.y >= contentSize.height - paddingToBottom;
        setIsAtBottom(isScrolledToBottom);
    };

    const handleContentSizeChange = () => {
        if (isAtBottom && scrollViewRef.current) {
            scrollViewRef.current.scrollToEnd({ animated: true });
        }
    };

    // --- 렌더링 (JSX) ---
    return (
        <SafeAreaProvider>
            <SafeAreaView style={{ flex: 1, backgroundColor: "#fff" }}>
                <View style={styles.header}>
                    <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
                        <Text style={styles.backButtonText}>{'<'}</Text>
                    </TouchableOpacity>
                    <Text style={styles.headerTitle}>Chat-Bot</Text>
                    <TouchableOpacity onPress={handleResetChat} style={styles.resetButton}>
                        <Image
                            source={require('../../assets/reset_icon.png')}
                            style={styles.resetIcon}
                        />
                    </TouchableOpacity>
                </View>
                <KeyboardAvoidingView
                    behavior={Platform.OS === "ios" ? "padding" : "height"}
                    style={{ flex: 1 }}
                    keyboardVerticalOffset={Platform.OS === "ios" ? 60 : 0}
                >
                    <ScrollView
                        ref={scrollViewRef}
                        style={styles.messagesContainer}
                        contentContainerStyle={{ paddingBottom: 20 }}
                        showsVerticalScrollIndicator={false}
                        keyboardShouldPersistTaps="handled"
                        onScroll={handleScroll}
                        scrollEventThrottle={16}
                        onContentSizeChange={handleContentSizeChange}
                    >
                        {messages.map((msg) =>
                            msg.type === "bot" ? (
                                <ChatBotMessage
                                    key={msg.id}
                                    message={msg}
                                    time={msg.time}
                                    quickReplies={msg.quickReplies}
                                    onQuickReplyPress={handleQuickReplyPress}
                                />
                            ) : (
                                <UserMessage key={msg.id} message={msg} time={msg.time} />
                            )
                        )}
                    </ScrollView>

                    <View style={styles.inputContainer}>
                        <View style={styles.inputWrapper}>
                            <TextInput
                                style={styles.textInput}
                                placeholder="메시지 입력"
                                value={inputText}
                                onChangeText={setInputText}
                                onSubmitEditing={() => sendMessage(inputText)}
                                returnKeyType="send"
                                multiline
                            />
                            <TouchableOpacity style={styles.sendButton} onPress={() => sendMessage(inputText)} disabled={!!animatingMessage}>
                                <Text style={styles.sendArrowText}>➤</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </KeyboardAvoidingView>
            </SafeAreaView>
        </SafeAreaProvider>
    );
};

const styles = StyleSheet.create({
    header: { flexDirection: 'row', alignItems: "center", justifyContent: "space-between", paddingVertical: 10, paddingHorizontal: 15, backgroundColor: "#fff", borderBottomWidth: 1, borderBottomColor: "#eee" },
    backButton: { padding: 5, minWidth: 40, alignItems: 'flex-start' },
    backButtonText: { fontSize: 24, fontWeight: 'bold', color: "#56B8FF" },
    headerTitle: { fontSize: 20, fontWeight: "bold", color: "#000" },
    resetButton: { minWidth: 40, alignItems: 'flex-end', padding: 5 },
    resetIcon: { width: 24, height: 24, tintColor: '#56B8FF', backgroundColor: 'transparent' },
    messagesContainer: { flex: 1, paddingHorizontal: 20, paddingTop: 20 },
    inputContainer: { borderTopWidth: 1, borderColor: "#e3e3e3", padding: 15, backgroundColor: "#fff" },
    inputWrapper: { flexDirection: "row", alignItems: "center" },
    textInput: { flex: 1, minHeight: 40, maxHeight: 120, fontSize: 14, color: "#000", backgroundColor: "#f9f9f9", borderRadius: 8, paddingHorizontal: 15, paddingTop: 10, paddingBottom: 10 },
    sendButton: { backgroundColor: "#56B8FF", width: 40, height: 40, borderRadius: 20, justifyContent: "center", alignItems: "center", marginLeft: 10, alignSelf: 'flex-end' },
    sendArrowText: { color: "#fff", fontSize: 16 },
});

export default ChatScreen;