import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ActivityIndicator, Alert } from 'react-native';
import apiClient from '../api/client';

const LoadingScreen = ({ navigation }) => {
    const [userKey, setUserKey] = useState("seungjae_key");

    useEffect(() => {
        const fetchData = async () => {
            if (!userKey) return;
            try {
                const response = await apiClient.post("/start-chat", { user_key: userKey });
                const initialMessages = response.data?.initialMessages;

                if (!initialMessages) {
                    throw new Error("초기 메시지 데이터가 없습니다.");
                }

                navigation.replace('Chat', { initialMessages: initialMessages });

            } catch (error) {
                console.error("초기 데이터 로딩 중 오류 발생:", error);
                
                Alert.alert(
                    "오류 발생",
                    "채팅방 입장에 실패했습니다. 잠시 후 다시 시도해주세요.",
                    [{ text: "확인", onPress: () => navigation.goBack() }]
                );
            }
        };

        if (userKey) {
            fetchData();
        }
    }, [userKey, navigation]);

    return (
        <SafeAreaView style={styles.container}>
            <ActivityIndicator size="large" color="#56B8FF" />
            <Text style={styles.text}>채팅방에 입장하는 중...</Text>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#fff',
    },
    text: {
        marginTop: 10,
        fontSize: 16,
        color: '#666',
    },
});

export default LoadingScreen;