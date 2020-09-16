using Discord;
using Discord.Webhook;
using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System.Data;

namespace omaha_watch_bot
{
    class Program
    {
        private string stableVersion, betaVersion, devVersion, canaryVersion;
        private DiscordWebhookClient mainClient;
        public static void Main(string[] args)
                => new Program().MainAsync().GetAwaiter().GetResult();

        public async Task MainAsync()
        {
            mainClient = new DiscordWebhookClient("link here");

            Console.WriteLine("Omaha Watch Bot is now active.");
            await FetchOmaha();
            await Task.Delay(Timeout.Infinite);
        }

        private async Task FetchOmaha()
        {
            WebClient client = new WebClient();
            stableVersion = betaVersion = devVersion = canaryVersion = "0";

            // This task will loop indefinitely.
            while (true)
            {
                StreamReader reader = new StreamReader(client.OpenRead("https://omahaproxy.appspot.com/all.json?os=win"));
                string content = reader.ReadToEnd();
                content = "{" + content[15..^1];
                //Console.WriteLine(content);

                DataSet dataSet = JsonConvert.DeserializeObject<DataSet>(content);
                DataTable dataTable = dataSet.Tables["versions"];

                EmbedBuilder embed = new EmbedBuilder();

                foreach (DataRow row in dataTable.Rows)
                {
                    //Console.WriteLine(row["channel"] + " - " + row["version"]);
                    if (row["channel"].Equals("canary"))
                    {
                        if (canaryVersion.Equals("0")) canaryVersion = row["version"].ToString();
                        else
                        {
                            if (!canaryVersion.Equals(row["version"].ToString()))
                            {
                                embed.Title = "Canary update available!";
                                embed.AddField("New version: ", row["version"].ToString(), false).WithColor(Color.DarkPurple);
                                await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                                canaryVersion = row["version"].ToString();
                            }
                        }
                    }
                    else if (row["channel"].Equals("dev"))
                    {
                        if (devVersion.Equals("0")) devVersion = row["version"].ToString();
                        else
                        {
                            if (!devVersion.Equals(row["version"].ToString()))
                            {
                                embed.Title = "Dev update available!";
                                embed.AddField("New version: ", row["version"].ToString(), false).WithColor(Color.Red);
                                await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                                devVersion = row["version"].ToString();
                            }
                        }
                    }
                    else if (row["channel"].Equals("beta"))
                    {
                        if (betaVersion.Equals("0")) betaVersion = row["version"].ToString();
                        else
                        {
                            if (!betaVersion.Equals(row["version"].ToString()))
                            {
                                embed.Title = "Beta update available!";
                                embed.AddField("New version: ", row["version"].ToString(), false).WithColor(Color.Gold);
                                await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                                betaVersion = row["version"].ToString();
                            }
                        }
                    }
                    else if (row["channel"].Equals("stable"))
                    {
                        if (stableVersion.Equals("0")) stableVersion = row["version"].ToString();
                        else
                        {
                            if (!stableVersion.Equals(row["version"].ToString()))
                            {
                                embed.Title = "Stable update available!";
                                embed.AddField("New version: ", row["version"].ToString(), false).WithColor(Color.Green);
                                await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                                stableVersion = row["version"].ToString();
                            }
                        }
                    }
                }

                await Task.Delay(1800000);
            }
           
        }
    }
}
