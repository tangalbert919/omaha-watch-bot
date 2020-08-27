using Discord;
using Discord.Webhook;
using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Data;
using System.Collections.Generic;

namespace omaha_watch_bot
{
    class Program
    {
        private string stableVersion, betaVersion, devVersion, canaryVersion = "0";
        private DiscordWebhookClient mainClient;
        public static void Main(string[] args)
                => new Program().MainAsync().GetAwaiter().GetResult();

        public async Task MainAsync()
        {
            mainClient = new DiscordWebhookClient("link here");

            await fetchOmaha();
            await Task.Delay(Timeout.Infinite);
        }

        private async Task fetchOmaha()
        {
            WebClient client = new WebClient();
            EmbedBuilder embed = new EmbedBuilder();

            // This task will loop indefinitely.
            // TODO: Complete this loop.
            while (true)
            {
                StreamReader reader = new StreamReader(client.OpenRead("https://omahaproxy.appspot.com/all.json?os=win"));
                string content = reader.ReadToEnd();
                Console.WriteLine(content);

                JsonTextReader jsonTextReader = new JsonTextReader(reader);

                JObject o1 = (JObject)JToken.ReadFrom(jsonTextReader);
                stableVersion = o1.Children().ToString();
                Console.WriteLine(stableVersion);
                
                embed.Title = "Test embed";
                //await mainClient.SendMessageAsync(embeds: new[] { embed.Build() });
                await Task.Delay(5000);
            }
           
        }
    }
}
