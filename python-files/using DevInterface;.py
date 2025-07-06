using DevInterface;
using RWCustom;
using UnityEngine;

public class ScavengerChiefArenaSpawner
{
    public static void Apply()
    {
        On.ArenaMenu.ctor += ArenaMenu_ctor;
    }

    private static void ArenaMenu_ctor(On.ArenaMenu.orig_ctor orig, ArenaMenu self, ProcessManager manager, RainWorldGame game)
    {
        orig(self, manager, game);

        // Создаем новую кнопку для вождя мусорщиков
        SimpleButton scavengerChiefButton = new SimpleButton(self, self.pages[0], "ScavengerChiefButton", "Scavenger Chief", "", new Vector2(50f, 50f), new Vector2(120f, 30f));
        self.pages[0].subObjects.Add(scavengerChiefButton);
        self.buttons.Add(scavengerChiefButton);

        // Добавляем обработчик нажатия на кнопку
        scavengerChiefButton.OnClick += () =>
        {
            // Создаем существо вождя мусорщиков.  Используем имя существа из файлов игры
            AbstractCreature abstractCreature = new AbstractCreature(self.game.world, StaticWorld.GetCreatureTemplate(CreatureTemplate.Type.Scavenger), null, self.game.world.GetRandomRoom().GetWorldCoordinate(Vector2.zero), self.game.GetNewID());
            abstractCreature.RealizeInRoom(); // Создаем физическое представление существа в комнате
            (abstractCreature.realizedObject as Scavenger).chief = true;

        };

        // Загружаем иконку для кнопки (предполагается, что она есть в атласе игры)
        // TODO: тут нужно указать имя спрайта из атласа, если есть. Иначе, стандартная иконка.
        //string iconName = "ScavengerChiefIcon";
        //scavengerChiefButton.myImage.sprite = Futile.atlasManager.GetSprite(iconName);

    }
}
