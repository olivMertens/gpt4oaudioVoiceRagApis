import React, { useState, useEffect } from "react";

interface VoiceSelectorProps {
    selectedVoice: string;
    onVoiceChange: (voice: string) => void;
}

const VoiceSelector: React.FC<VoiceSelectorProps> = ({ selectedVoice, onVoiceChange }) => {
    const [availableVoices, setAvailableVoices] = useState<string[]>([]);

    useEffect(() => {
        const fetchAvailableVoices = async () => {
            try {
                const response = await fetch(`${import.meta.env.VITE_AZURE_API_ENDPOINT}/api/available-voices`);
                const data = await response.json();
                setAvailableVoices(data.voices);
            } catch (error) {
                console.error("Failed to fetch available voices:", error);
            }
        };

        fetchAvailableVoices();
    }, []);

    const handleVoiceChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
        const newVoice = event.target.value;
        onVoiceChange(newVoice);

        try {
            const response = await fetch(`${import.meta.env.VITE_AZURE_API_ENDPOINT}/api/voice`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ voice: newVoice })
            });

            if (!response.ok) {
                throw new Error("Failed to update voice choice");
            }
        } catch (error) {
            console.error("Failed to update voice choice:", error);
        }
    };

    return (
        <div>
            <label htmlFor="voice-selector">Select Voice:</label>
            <select id="voice-selector" value={selectedVoice} onChange={handleVoiceChange}>
                {availableVoices.map(voice => (
                    <option key={voice} value={voice}>
                        {voice}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default VoiceSelector;
