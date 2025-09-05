import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import Markdown from 'react-native-markdown-display';

const ChatBotMessage = ({ message, time, quickReplies, onQuickReplyPress }) => (
    <View style={styles.chatBotMessageContainer}>
        <View style={styles.chatBotAvatar}>
            <Image source={require('../../assets/ChatBotIcon.png')} style={styles.avatarText} />
        </View>
        <View style={styles.chatBotMessageWrapper}>
            <View style={styles.chatBotMessageBubble}>
              <Markdown style={markdownStyles}>{message.text}</Markdown>
                {quickReplies && quickReplies.length > 0 && (
                    <View style={styles.quickRepliesWrapper}>
                        {quickReplies.map((q, i) => (
                            <TouchableOpacity key={i} style={styles.quickReplyButton} onPress={() => onQuickReplyPress(q)}>
                                <Text style={styles.quickReplyText}>{q}</Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                )}
            </View>
            <Text style={styles.messageTime}>{time}</Text>
        </View>
    </View>
);

const markdownStyles = StyleSheet.create({
    heading3: { fontSize: 16, fontWeight: 'bold', color: '#000', marginBottom: 8, marginTop: 8 },
    strong: { fontWeight: 'bold' },
    body: { fontSize: 14, color: '#000' },
    bullet_list: { marginBottom: 8 },
    list_item: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 4 },
});

const styles = StyleSheet.create({
    chatBotMessageContainer: { flexDirection: "row", marginBottom: 20 },
    chatBotAvatar: { width: 50, height: 50, borderRadius: 5, justifyContent: "center", alignItems: "center", marginRight: 10 },
    avatarText: { width: 50, height: 50 },
    chatBotMessageWrapper: { flex: 1 },
    chatBotMessageBubble: { backgroundColor: "#F1F1F1", borderRadius: 10, padding: 12 },
    quickRepliesWrapper: { marginTop: 10, flexDirection: "row", flexWrap: "wrap" },
    quickReplyButton: { backgroundColor: "#fff", borderRadius: 20, paddingVertical: 8, paddingHorizontal: 14, margin: 4, borderWidth: 1, borderColor: "#CFCFCF" },
    quickReplyText: { fontSize: 12, color: "#000" },
    messageTime: { fontSize: 10, color: "#888", marginTop: 5 },
});

export default ChatBotMessage;