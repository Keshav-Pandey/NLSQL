using MySql.Data.MySqlClient;
using System;
using System.Collections.Generic;
using System.Data.Common;
using System.Linq;
using System.Threading.Tasks;

namespace NLSQL
{
    public class DB
    {
        private MySqlConnection connection;
        private string server;
        private string database;
        private string user;
        private string password;
        private string port;
        private string connectionString;
        private string sslM;
        public DB() {
            server = "hr.clurfavlxnya.us-west-2.rds.amazonaws.com";
            database = "hr";
            user = "admin";
            password = "1amAdmin";
            port = "3306";
            sslM = "none";
            connectionString = String.Format("server={0};port={1};user id={2}; password={3}; database={4}; SslMode={5}", server, port, user, password, database, sslM);
            connection = new MySqlConnection(connectionString);
        }

        public string conTest()
        {
            try
            {
                connection.Open();

                System.Diagnostics.Debug.Write("successful connection");

                connection.Close();
                return "worked";
            }
            catch (MySqlException ex)
            {
                System.Diagnostics.Debug.Write(ex.Message + connectionString);
                return "did not work";
            }
        }

        public string runOneLineQuery(string query)
        {
            try
            {
                connection.Open();
                string output = "";
                var cmd = new MySqlCommand(query, connection);
                var reader = cmd.ExecuteReader();
                while (reader.Read())
                {
                    for(int i=0; i < reader.VisibleFieldCount; i++)
                        output += reader.GetString(i) + " ";
                }
                connection.Close();
                return output;
            }
            catch (MySqlException ex)
            {
                System.Diagnostics.Debug.Write(ex.Message + connectionString);
                return "did not work";
            }
        }
    }
}
