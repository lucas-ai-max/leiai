-- Create dedicated Salesforce project
-- This project will be used exclusively for Salesforce imports
-- ID: 00000000-0000-0000-0000-000000000001

INSERT INTO projeto (id, nome)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Importações Salesforce'
)
ON CONFLICT (id) DO NOTHING;
