-- Drop existing foreign key constraint
ALTER TABLE chat_feedback
    DROP CONSTRAINT IF EXISTS chat_feedback_message_uuid_fkey;

-- Recreate foreign key with CASCADE
ALTER TABLE chat_feedback
    ADD CONSTRAINT chat_feedback_message_uuid_fkey
    FOREIGN KEY (message_uuid)
    REFERENCES chat_history(message_uuid)
    ON DELETE CASCADE;
