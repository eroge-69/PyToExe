using System;
using System.Diagnostics;
using System.IO;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("Creating Steam store...");
        CreateSteamStore();
        Console.WriteLine("Steam store created!");

        string game = GetRandomGame();
        Console.WriteLine($"Opening {game} page...");
        OpenSteamPage(game);

        Console.WriteLine("Game opened. Downloading...");
        DownloadGame(game);

        Console.WriteLine("Your computer has been hacked!");
        Console.WriteLine("Shutting down...");
        ShutdownComputer();
    }

    static void CreateSteamStore()
    {
        string[] games = { "Garry's Mod", "Counter-Strike: Global Offensive", "Stalker: Shadow of Chernobyl" };
        foreach (string game in games)
        {
            Directory.CreateDirectory(game);
            File.WriteAllText($"{game}/README.md", $"# {game}\n\nA great game!");
        }
    }

    static string GetRandomGame()
    {
        string[] games = { "Garry's Mod", "Counter-Strike: Global Offensive", "Stalker: Shadow of Chernobyl" };
        Random random = new Random();
        return games[random.Next(games.Length)];
    }

    static void OpenSteamPage(string game)
    {
        Process.Start($"https://store.steampowered.com/app/{new Random().Next(1000, 9999)}/{game.Replace(" ", "_")}");
    }

    static void DownloadGame(string game)
    {
        Console.WriteLine($"Downloading {game}...");
        System.Threading.Thread.Sleep(2000);
        Console.WriteLine($"{game} downloaded!");
    }

    static void ShutdownComputer()
    {
        Process.Start("shutdown", "/s /t 1");
    }
}