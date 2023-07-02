using Discord;
using Discord.Webhook;
using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text.Json.Nodes;

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
            HttpClient http = new();
            stableVersion = betaVersion = devVersion = canaryVersion = "0";
            // Exists for debugging reasons.
            canaryVersion = "114.0.5175.0";
            await Task.Delay(1000);

            // This task will loop indefinitely.
            while (true)
            {
                using HttpResponseMessage message = await http.GetAsync("https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/all/versions/all/releases?filter=endtime=none&order_by=fraction%20desc");
                message.EnsureSuccessStatusCode();
                Stream responseBody = await message.Content.ReadAsStreamAsync();
                StreamReader reader = new(responseBody);
                string content = reader.ReadToEnd();

                JsonNode releaseNode = JsonNode.Parse(content);
                JsonArray releases = releaseNode["releases"].AsArray();
                //Console.WriteLine(releases[0]);
                EmbedBuilder embed = new();

                foreach (JsonNode release in releases)
                {
                    //Console.WriteLine(release["version"]);
                    if (release["name"].ToString().Contains("/canary/")) // Avoid canary_asan, separate channel
                    {
                        if (canaryVersion.Equals("0")) canaryVersion = release["version"].ToString();
                        else if (!canaryVersion.Equals(release["version"].ToString()))
                        {
                            embed.Title = "Canary update available!";
                            embed.AddField("New version: ", release["version"].ToString(), false).WithColor(Color.DarkPurple);
                            await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                            canaryVersion = release["version"].ToString();
                        }
                    }
                    else if (release["name"].ToString().Contains("dev"))
                    {
                        if (devVersion.Equals("0")) devVersion = release["version"].ToString();
                        else if (!devVersion.Equals(release["version"].ToString()))
                        {
                            embed.Title = "Dev update available!";
                            embed.AddField("New version: ", release["version"].ToString(), false).WithColor(Color.Red);
                            await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                            devVersion = release["version"].ToString();
                        }
                    }
                    else if (release["name"].ToString().Contains("beta"))
                    {
                        if (betaVersion.Equals("0")) betaVersion = release["version"].ToString();
                        else if (!betaVersion.Equals(release["version"].ToString()))
                        {
                            embed.Title = "Beta update available!";
                            embed.AddField("New version: ", release["version"].ToString(), false).WithColor(Color.Gold);
                            await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                            betaVersion = release["version"].ToString();
                        }
                    }
                    else if (release["name"].ToString().Contains("stable"))
                    {
                        if (stableVersion.Equals("0")) stableVersion = release["version"].ToString();
                        else if (!stableVersion.Equals(release["version"].ToString()))
                        {
                            embed.Title = "Stable update available!";
                            embed.AddField("New version: ", release["version"].ToString(), false).WithColor(Color.Green);
                            await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                            stableVersion = release["version"].ToString();
                        }
                    }
                }
                await Task.Delay(1800000);
            }
           
        }
    }
}
