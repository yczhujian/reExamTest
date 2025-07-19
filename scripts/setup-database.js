const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env.local') });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase environment variables');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function setupDatabase() {
  try {
    console.log('Setting up database schema...');
    
    // Read the schema file
    const schemaPath = path.join(__dirname, '../database/schema.sql');
    const schema = fs.readFileSync(schemaPath, 'utf8');
    
    // Note: Supabase doesn't support running raw SQL through the client library
    // You'll need to run this SQL directly in the Supabase SQL editor
    console.log('Please run the following SQL in your Supabase SQL editor:');
    console.log('https://supabase.com/dashboard/project/grjslrfvlarfslgtoeqi/editor');
    console.log('\n--- COPY SQL BELOW ---\n');
    console.log(schema);
    console.log('\n--- END SQL ---\n');
    
    console.log('After running the SQL, your database will be ready!');
  } catch (error) {
    console.error('Error setting up database:', error);
    process.exit(1);
  }
}

setupDatabase();