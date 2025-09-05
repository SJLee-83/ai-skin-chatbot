import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const UserMessage = ({ message, time }) => (
    <View style={styles.userMessageContainer}>
        <View style={styles.userMessageWrapper}>
            <View style={styles.userMessageBubble}>
                <Text style={styles.userMessageText}>{message.text}</Text>
            </View>
            <Text style={styles.userMessageTime}>{time}</Text>
        </View>
    </View>
);

const styles = StyleSheet.create({
    userMessageContainer: {
        alignItems: "flex-end",
        marginBottom: 20,
    },
    userMessageWrapper: {
        alignItems: "flex-end",
    },
    userMessageBubble: {
        backgroundColor: "#B5F8FF",
        borderRadius: 10,
        padding: 12,
        maxWidth: "85%",
    },
    userMessageText: {
        fontSize: 14,
        color: "#000",
    },
    userMessageTime: {
        fontSize: 10,
        color: "#888",
        marginTop: 5,
    },
});

export default UserMessage;