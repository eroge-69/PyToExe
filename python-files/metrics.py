import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

def generate_markdown_comment(input_date, utc_offset):
    # Парсим входную дату (без времени)
    base_date = datetime.strptime(input_date, '%m-%Y')
    
    # Корректируем даты с учетом UTC offset
    
    # 1. Первый день текущего месяца (00:00:00) с учетом UTC
    first_day_current = (base_date.replace(day=1, hour=0, minute=0, second=0) 
                        - timedelta(hours=utc_offset))
    
    # 2. Последний день текущего месяца (23:59:59) с учетом UTC
    next_month = base_date.replace(day=28) + timedelta(days=4)
    last_day_current = (next_month - timedelta(days=next_month.day))
    current_month_end = (last_day_current.replace(hour=23, minute=59, second=59) 
                        - timedelta(hours=utc_offset))
    
    # 3. Последний день предыдущего месяца (23:59:59) с учетом UTC
    last_month_end = ((base_date.replace(day=1) - timedelta(days=1)).replace(hour=23, minute=59, second=59) 
                     - timedelta(hours=utc_offset))
    
    # Форматируем даты для SQL
    current_month_end_str = current_month_end.strftime('%Y-%m-%d %H:%M:%S')
    last_month_end_str = last_month_end.strftime('%Y-%m-%d %H:%M:%S')
    first_day_current_str = first_day_current.strftime('%Y-%m-%d %H:%M:%S')
    
    # Исходный SQL-запрос
    sql_template = """
>**1) Общий отчет**

```sql
SELECT
    pgm_au.AU AS 'AU',
    pgm_newau.NewAU AS 'New AU',
    pgm_aulastmonth.AULastMonth AS 'Last Month AU',
    pgm_aulastcurrent.AULastCurrent AS 'Last-Current AU'
FROM
(
    SELECT COUNT(DISTINCT f_player_id) AS AU
    FROM t_analytics_players_games_monthly
    WHERE
        (IFNULL(f_count_games_35,0) <> 0 OR IFNULL(f_count_games_54,0) <> 0 OR IFNULL(f_count_games_65,0) <> 0 OR IFNULL(f_count_games_66,0) <> 0 OR IFNULL(f_count_games_67,0) <> 0 OR IFNULL(f_count_games_68,0) <> 0 OR IFNULL(f_count_games_69,0) <> 0 OR IFNULL(f_count_games_70,0) <> 0 OR IFNULL(f_count_games_71,0) <> 0 OR IFNULL(f_count_games_72,0) <> 0 OR IFNULL(f_count_games_73,0) <> 0 OR IFNULL(f_count_games_74,0) <> 0 OR IFNULL(f_count_games_75,0) <> 0 OR IFNULL(f_count_games_76,0) <> 0 OR IFNULL(f_count_games_77,0) <> 0 OR IFNULL(f_count_games_78,0) <> 0 OR IFNULL(f_count_games_79,0) <> 0 OR IFNULL(f_count_games_80,0) <> 0 OR IFNULL(f_count_games_81,0) <> 0 OR IFNULL(f_count_games_82,0) <> 0 OR IFNULL(f_count_games_83,0) <> 0 OR IFNULL(f_count_games_84,0) <> 0 OR IFNULL(f_count_games_85,0) <> 0 OR IFNULL(f_count_games_86,0) <> 0 OR IFNULL(f_count_games_87,0) <> 0 OR IFNULL(f_count_games_88,0) <> 0 OR IFNULL(f_count_games_89,0) <> 0 OR IFNULL(f_count_games_90,0) <> 0 OR IFNULL(f_count_games_91,0) <> 0 OR IFNULL(f_count_games_92,0) <> 0 OR IFNULL(f_count_games_93,0) <> 0 OR IFNULL(f_count_games_94,0) <> 0 OR IFNULL(f_count_games_95,0) <> 0 OR IFNULL(f_count_games_96,0) <> 0 OR IFNULL(f_count_games_97,0) <> 0 OR IFNULL(f_count_games_98,0) <> 0 OR IFNULL(f_count_games_99,0) <> 0 OR IFNULL(f_count_games_34,0) <> 0 OR IFNULL(f_count_games_55,0) <> 0 OR IFNULL(f_count_games_63,0) <> 0 OR IFNULL(f_count_games_64,0) <> 0 OR IFNULL(f_count_games_100,0) <> 0 OR IFNULL(f_count_games_101,0) <> 0 OR IFNULL(f_count_games_102,0) <> 0 OR IFNULL(f_count_games_103,0) <> 0 OR IFNULL(f_count_games_104,0) <> 0 OR IFNULL(f_count_games_105,0) <> 0 OR IFNULL(f_count_games_106,0) <> 0 OR IFNULL(f_count_games_107,0) <> 0 OR IFNULL(f_count_games_108,0) <> 0 OR IFNULL(f_count_games_109,0) <> 0 OR IFNULL(f_count_games_110,0) <> 0)
        AND f_timestamp = 'CURRENT_MONTH_END'
) AS pgm_au,
(
    SELECT COUNT(DISTINCT f_player_id) AS NewAU
    FROM t_analytics_players_games_monthly
    WHERE
        f_player_id IN (SELECT f_id FROM t_player WHERE f_register_stamp BETWEEN 'FIRST_DAY_CURRENT' AND 'CURRENT_MONTH_END')
        AND f_timestamp = 'CURRENT_MONTH_END'
        AND (IFNULL(f_count_games_35,0) <> 0 OR IFNULL(f_count_games_54,0) <> 0 OR IFNULL(f_count_games_65,0) <> 0 OR IFNULL(f_count_games_66,0) <> 0 OR IFNULL(f_count_games_67,0) <> 0 OR IFNULL(f_count_games_68,0) <> 0 OR IFNULL(f_count_games_69,0) <> 0 OR IFNULL(f_count_games_70,0) <> 0 OR IFNULL(f_count_games_71,0) <> 0 OR IFNULL(f_count_games_72,0) <> 0 OR IFNULL(f_count_games_73,0) <> 0 OR IFNULL(f_count_games_74,0) <> 0 OR IFNULL(f_count_games_75,0) <> 0 OR IFNULL(f_count_games_76,0) <> 0 OR IFNULL(f_count_games_77,0) <> 0 OR IFNULL(f_count_games_78,0) <> 0 OR IFNULL(f_count_games_79,0) <> 0 OR IFNULL(f_count_games_80,0) <> 0 OR IFNULL(f_count_games_81,0) <> 0 OR IFNULL(f_count_games_82,0) <> 0 OR IFNULL(f_count_games_83,0) <> 0 OR IFNULL(f_count_games_84,0) <> 0 OR IFNULL(f_count_games_85,0) <> 0 OR IFNULL(f_count_games_86,0) <> 0 OR IFNULL(f_count_games_87,0) <> 0 OR IFNULL(f_count_games_88,0) <> 0 OR IFNULL(f_count_games_89,0) <> 0 OR IFNULL(f_count_games_90,0) <> 0 OR IFNULL(f_count_games_91,0) <> 0 OR IFNULL(f_count_games_92,0) <> 0 OR IFNULL(f_count_games_93,0) <> 0 OR IFNULL(f_count_games_94,0) <> 0 OR IFNULL(f_count_games_95,0) <> 0 OR IFNULL(f_count_games_96,0) <> 0 OR IFNULL(f_count_games_97,0) <> 0 OR IFNULL(f_count_games_98,0) <> 0 OR IFNULL(f_count_games_99,0) <> 0 OR IFNULL(f_count_games_34,0) <> 0 OR IFNULL(f_count_games_55,0) <> 0 OR IFNULL(f_count_games_63,0) <> 0 OR IFNULL(f_count_games_64,0) <> 0 OR IFNULL(f_count_games_100,0) <> 0 OR IFNULL(f_count_games_101,0) <> 0 OR IFNULL(f_count_games_102,0) <> 0 OR IFNULL(f_count_games_103,0) <> 0 OR IFNULL(f_count_games_104,0) <> 0 OR IFNULL(f_count_games_105,0) <> 0 OR IFNULL(f_count_games_106,0) <> 0 OR IFNULL(f_count_games_107,0) <> 0 OR IFNULL(f_count_games_108,0) <> 0 OR IFNULL(f_count_games_109,0) <> 0 OR IFNULL(f_count_games_110,0) <> 0)

) AS pgm_newau,
(
    SELECT COUNT(DISTINCT f_player_id) AS AULastMonth
    FROM t_analytics_players_games_monthly
    WHERE
        (IFNULL(f_count_games_35,0) <> 0 OR IFNULL(f_count_games_54,0) <> 0 OR IFNULL(f_count_games_65,0) <> 0 OR IFNULL(f_count_games_66,0) <> 0 OR IFNULL(f_count_games_67,0) <> 0 OR IFNULL(f_count_games_68,0) <> 0 OR IFNULL(f_count_games_69,0) <> 0 OR IFNULL(f_count_games_70,0) <> 0 OR IFNULL(f_count_games_71,0) <> 0 OR IFNULL(f_count_games_72,0) <> 0 OR IFNULL(f_count_games_73,0) <> 0 OR IFNULL(f_count_games_74,0) <> 0 OR IFNULL(f_count_games_75,0) <> 0 OR IFNULL(f_count_games_76,0) <> 0 OR IFNULL(f_count_games_77,0) <> 0 OR IFNULL(f_count_games_78,0) <> 0 OR IFNULL(f_count_games_79,0) <> 0 OR IFNULL(f_count_games_80,0) <> 0 OR IFNULL(f_count_games_81,0) <> 0 OR IFNULL(f_count_games_82,0) <> 0 OR IFNULL(f_count_games_83,0) <> 0 OR IFNULL(f_count_games_84,0) <> 0 OR IFNULL(f_count_games_85,0) <> 0 OR IFNULL(f_count_games_86,0) <> 0 OR IFNULL(f_count_games_87,0) <> 0 OR IFNULL(f_count_games_88,0) <> 0 OR IFNULL(f_count_games_89,0) <> 0 OR IFNULL(f_count_games_90,0) <> 0 OR IFNULL(f_count_games_91,0) <> 0 OR IFNULL(f_count_games_92,0) <> 0 OR IFNULL(f_count_games_93,0) <> 0 OR IFNULL(f_count_games_94,0) <> 0 OR IFNULL(f_count_games_95,0) <> 0 OR IFNULL(f_count_games_96,0) <> 0 OR IFNULL(f_count_games_97,0) <> 0 OR IFNULL(f_count_games_98,0) <> 0 OR IFNULL(f_count_games_99,0) <> 0 OR IFNULL(f_count_games_34,0) <> 0 OR IFNULL(f_count_games_55,0) <> 0 OR IFNULL(f_count_games_63,0) <> 0 OR IFNULL(f_count_games_64,0) <> 0 OR IFNULL(f_count_games_100,0) <> 0 OR IFNULL(f_count_games_101,0) <> 0 OR IFNULL(f_count_games_102,0) <> 0 OR IFNULL(f_count_games_103,0) <> 0 OR IFNULL(f_count_games_104,0) <> 0 OR IFNULL(f_count_games_105,0) <> 0 OR IFNULL(f_count_games_106,0) <> 0 OR IFNULL(f_count_games_107,0) <> 0 OR IFNULL(f_count_games_108,0) <> 0 OR IFNULL(f_count_games_109,0) <> 0 OR IFNULL(f_count_games_110,0) <> 0)
        AND f_timestamp = 'LAST_MONTH_END'
) AS pgm_aulastmonth,
(
    SELECT COUNT(DISTINCT f_player_id) AS AULastCurrent
    FROM t_analytics_players_games_monthly
    WHERE
        f_player_id IN (
            SELECT f_player_id
            FROM t_analytics_players_games_monthly
            WHERE f_timestamp = 'CURRENT_MONTH_END'
            AND (IFNULL(f_count_games_35,0) <> 0 OR IFNULL(f_count_games_54,0) <> 0 OR IFNULL(f_count_games_65,0) <> 0 OR IFNULL(f_count_games_66,0) <> 0 OR IFNULL(f_count_games_67,0) <> 0 OR IFNULL(f_count_games_68,0) <> 0 OR IFNULL(f_count_games_69,0) <> 0 OR IFNULL(f_count_games_70,0) <> 0 OR IFNULL(f_count_games_71,0) <> 0 OR IFNULL(f_count_games_72,0) <> 0 OR IFNULL(f_count_games_73,0) <> 0 OR IFNULL(f_count_games_74,0) <> 0 OR IFNULL(f_count_games_75,0) <> 0 OR IFNULL(f_count_games_76,0) <> 0 OR IFNULL(f_count_games_77,0) <> 0 OR IFNULL(f_count_games_78,0) <> 0 OR IFNULL(f_count_games_79,0) <> 0 OR IFNULL(f_count_games_80,0) <> 0 OR IFNULL(f_count_games_81,0) <> 0 OR IFNULL(f_count_games_82,0) <> 0 OR IFNULL(f_count_games_83,0) <> 0 OR IFNULL(f_count_games_84,0) <> 0 OR IFNULL(f_count_games_85,0) <> 0 OR IFNULL(f_count_games_86,0) <> 0 OR IFNULL(f_count_games_87,0) <> 0 OR IFNULL(f_count_games_88,0) <> 0 OR IFNULL(f_count_games_89,0) <> 0 OR IFNULL(f_count_games_90,0) <> 0 OR IFNULL(f_count_games_91,0) <> 0 OR IFNULL(f_count_games_92,0) <> 0 OR IFNULL(f_count_games_93,0) <> 0 OR IFNULL(f_count_games_94,0) <> 0 OR IFNULL(f_count_games_95,0) <> 0 OR IFNULL(f_count_games_96,0) <> 0 OR IFNULL(f_count_games_97,0) <> 0 OR IFNULL(f_count_games_98,0) <> 0 OR IFNULL(f_count_games_99,0) <> 0 OR IFNULL(f_count_games_34,0) <> 0 OR IFNULL(f_count_games_55,0) <> 0 OR IFNULL(f_count_games_63,0) <> 0 OR IFNULL(f_count_games_64,0) <> 0 OR IFNULL(f_count_games_100,0) <> 0 OR IFNULL(f_count_games_101,0) <> 0 OR IFNULL(f_count_games_102,0) <> 0 OR IFNULL(f_count_games_103,0) <> 0 OR IFNULL(f_count_games_104,0) <> 0 OR IFNULL(f_count_games_105,0) <> 0 OR IFNULL(f_count_games_106,0) <> 0 OR IFNULL(f_count_games_107,0) <> 0 OR IFNULL(f_count_games_108,0) <> 0 OR IFNULL(f_count_games_109,0) <> 0 OR IFNULL(f_count_games_110,0) <> 0)
        )
        AND f_player_id IN (
            SELECT f_player_id
            FROM t_analytics_players_games_monthly
            WHERE f_timestamp = 'LAST_MONTH_END'
            AND (IFNULL(f_count_games_35,0) <> 0 OR IFNULL(f_count_games_54,0) <> 0 OR IFNULL(f_count_games_65,0) <> 0 OR IFNULL(f_count_games_66,0) <> 0 OR IFNULL(f_count_games_67,0) <> 0 OR IFNULL(f_count_games_68,0) <> 0 OR IFNULL(f_count_games_69,0) <> 0 OR IFNULL(f_count_games_70,0) <> 0 OR IFNULL(f_count_games_71,0) <> 0 OR IFNULL(f_count_games_72,0) <> 0 OR IFNULL(f_count_games_73,0) <> 0 OR IFNULL(f_count_games_74,0) <> 0 OR IFNULL(f_count_games_75,0) <> 0 OR IFNULL(f_count_games_76,0) <> 0 OR IFNULL(f_count_games_77,0) <> 0 OR IFNULL(f_count_games_78,0) <> 0 OR IFNULL(f_count_games_79,0) <> 0 OR IFNULL(f_count_games_80,0) <> 0 OR IFNULL(f_count_games_81,0) <> 0 OR IFNULL(f_count_games_82,0) <> 0 OR IFNULL(f_count_games_83,0) <> 0 OR IFNULL(f_count_games_84,0) <> 0 OR IFNULL(f_count_games_85,0) <> 0 OR IFNULL(f_count_games_86,0) <> 0 OR IFNULL(f_count_games_87,0) <> 0 OR IFNULL(f_count_games_88,0) <> 0 OR IFNULL(f_count_games_89,0) <> 0 OR IFNULL(f_count_games_90,0) <> 0 OR IFNULL(f_count_games_91,0) <> 0 OR IFNULL(f_count_games_92,0) <> 0 OR IFNULL(f_count_games_93,0) <> 0 OR IFNULL(f_count_games_94,0) <> 0 OR IFNULL(f_count_games_95,0) <> 0 OR IFNULL(f_count_games_96,0) <> 0 OR IFNULL(f_count_games_97,0) <> 0 OR IFNULL(f_count_games_98,0) <> 0 OR IFNULL(f_count_games_99,0) <> 0 OR IFNULL(f_count_games_34,0) <> 0 OR IFNULL(f_count_games_55,0) <> 0 OR IFNULL(f_count_games_63,0) <> 0 OR IFNULL(f_count_games_64,0) <> 0 OR IFNULL(f_count_games_100,0) <> 0 OR IFNULL(f_count_games_101,0) <> 0 OR IFNULL(f_count_games_102,0) <> 0 OR IFNULL(f_count_games_103,0) <> 0 OR IFNULL(f_count_games_104,0) <> 0 OR IFNULL(f_count_games_105,0) <> 0 OR IFNULL(f_count_games_106,0) <> 0 OR IFNULL(f_count_games_107,0) <> 0 OR IFNULL(f_count_games_108,0) <> 0 OR IFNULL(f_count_games_109,0) <> 0 OR IFNULL(f_count_games_110,0) <> 0)
        )
) AS pgm_aulastcurrent
```

>**2) Отчет по кэш играм**

```sql
SELECT
    pmm.f_iso_code AS 'Currency',
    pmm_au.AU AS 'AU',
    tgm.TotalGames AS 'Total Hands',
    pmm.NetWinning AS 'Net Winnings',
    pgm_aulastmonth.AULastMonth AS AULastMonth,
    pgm_aulastcurrent.AULastCurrent AS AULastCurrent
FROM
(
    SELECT
        c.f_money_type,
        c.f_iso_code,
        ROUND((SUM(IFNULL(f_to_tables,0)) - SUM(IFNULL(f_from_tables,0))) / POW(10, c.f_precision), c.f_precision) AS NetWinning
    FROM t_analytics_players_money_monthly
    LEFT JOIN t_currency c on c.f_money_type = t_analytics_players_money_monthly.f_money_type 
    WHERE
        t_analytics_players_money_monthly.f_timestamp = 'CURRENT_MONTH_END'
        AND (IFNULL(f_rake_35, 0) <> 0 OR IFNULL(f_rake_54, 0) <> 0 OR IFNULL(f_rake_65, 0) <> 0 OR IFNULL(f_rake_66, 0) <> 0 OR IFNULL(f_rake_67, 0) <> 0 OR IFNULL(f_rake_68, 0) <> 0 OR IFNULL(f_rake_69, 0) <> 0 OR IFNULL(f_rake_70, 0) <> 0 OR IFNULL(f_rake_71, 0) <> 0 OR IFNULL(f_rake_72, 0) <> 0 OR IFNULL(f_rake_73, 0) <> 0 OR IFNULL(f_rake_74, 0) <> 0 OR IFNULL(f_rake_75, 0) <> 0 OR IFNULL(f_rake_76, 0) <> 0 OR IFNULL(f_rake_77, 0) <> 0 OR IFNULL(f_rake_78, 0) <> 0 OR IFNULL(f_rake_79, 0) <> 0 OR IFNULL(f_rake_80, 0) <> 0 OR IFNULL(f_rake_81, 0) <> 0 OR IFNULL(f_rake_82, 0) <> 0 OR IFNULL(f_rake_83, 0) <> 0 OR IFNULL(f_rake_84, 0) <> 0 OR IFNULL(f_rake_85, 0) <> 0 OR IFNULL(f_rake_86, 0) <> 0 OR IFNULL(f_rake_87, 0) <> 0 OR IFNULL(f_rake_88, 0) <> 0 OR IFNULL(f_rake_89, 0) <> 0 OR IFNULL(f_rake_90, 0) <> 0 OR IFNULL(f_rake_91, 0) <> 0 OR IFNULL(f_rake_92, 0) <> 0 OR IFNULL(f_rake_93, 0) <> 0 OR IFNULL(f_rake_94, 0) <> 0 OR IFNULL(f_rake_95, 0) <> 0 OR IFNULL(f_rake_96, 0) <> 0 OR IFNULL(f_rake_97, 0) <> 0 OR IFNULL(f_rake_98, 0) <> 0 OR IFNULL(f_rake_99, 0) <> 0 OR IFNULL(f_rake_34, 0) <> 0 OR IFNULL(f_rake_55, 0) <> 0 OR IFNULL(f_rake_100, 0) <> 0 OR IFNULL(f_rake_63, 0) <> 0 OR IFNULL(f_rake_64, 0) <> 0 OR IFNULL(f_rake_101, 0) <> 0 OR IFNULL(f_rake_102, 0) <> 0 OR IFNULL(f_rake_103, 0) <> 0 OR IFNULL(f_rake_104, 0) <> 0 OR IFNULL(f_rake_105, 0) <> 0 OR IFNULL(f_rake_106, 0) <> 0 OR IFNULL(f_rake_107, 0) <> 0 OR IFNULL(f_rake_108, 0) <> 0 OR IFNULL(f_rake_109, 0) <> 0 OR IFNULL(f_rake_110, 0) <> 0)
    GROUP BY f_money_type
) AS pmm
JOIN
(
    SELECT 
        f_money_type,
        COUNT(DISTINCT f_player_id) AS AU
    FROM t_analytics_players_money_monthly
    WHERE
        (IFNULL(f_rake_35, 0) <> 0 OR IFNULL(f_rake_54, 0) <> 0 OR IFNULL(f_rake_65, 0) <> 0 OR IFNULL(f_rake_66, 0) <> 0 OR IFNULL(f_rake_67, 0) <> 0 OR IFNULL(f_rake_68, 0) <> 0 OR IFNULL(f_rake_69, 0) <> 0 OR IFNULL(f_rake_70, 0) <> 0 OR IFNULL(f_rake_71, 0) <> 0 OR IFNULL(f_rake_72, 0) <> 0 OR IFNULL(f_rake_73, 0) <> 0 OR IFNULL(f_rake_74, 0) <> 0 OR IFNULL(f_rake_75, 0) <> 0 OR IFNULL(f_rake_76, 0) <> 0 OR IFNULL(f_rake_77, 0) <> 0 OR IFNULL(f_rake_78, 0) <> 0 OR IFNULL(f_rake_79, 0) <> 0 OR IFNULL(f_rake_80, 0) <> 0 OR IFNULL(f_rake_81, 0) <> 0 OR IFNULL(f_rake_82, 0) <> 0 OR IFNULL(f_rake_83, 0) <> 0 OR IFNULL(f_rake_84, 0) <> 0 OR IFNULL(f_rake_85, 0) <> 0 OR IFNULL(f_rake_86, 0) <> 0 OR IFNULL(f_rake_87, 0) <> 0 OR IFNULL(f_rake_88, 0) <> 0 OR IFNULL(f_rake_89, 0) <> 0 OR IFNULL(f_rake_90, 0) <> 0 OR IFNULL(f_rake_91, 0) <> 0 OR IFNULL(f_rake_92, 0) <> 0 OR IFNULL(f_rake_93, 0) <> 0 OR IFNULL(f_rake_94, 0) <> 0 OR IFNULL(f_rake_95, 0) <> 0 OR IFNULL(f_rake_96, 0) <> 0 OR IFNULL(f_rake_97, 0) <> 0 OR IFNULL(f_rake_98, 0) <> 0 OR IFNULL(f_rake_99, 0) <> 0 OR IFNULL(f_rake_34, 0) <> 0 OR IFNULL(f_rake_55, 0) <> 0 OR IFNULL(f_rake_100, 0) <> 0 OR IFNULL(f_rake_63, 0) <> 0 OR IFNULL(f_rake_64, 0) <> 0 OR IFNULL(f_rake_101, 0) <> 0 OR IFNULL(f_rake_102, 0) <> 0 OR IFNULL(f_rake_103, 0) <> 0 OR IFNULL(f_rake_104, 0) <> 0 OR IFNULL(f_rake_105, 0) <> 0 OR IFNULL(f_rake_106, 0) <> 0 OR IFNULL(f_rake_107, 0) <> 0 OR IFNULL(f_rake_108, 0) <> 0 OR IFNULL(f_rake_109, 0) <> 0 OR IFNULL(f_rake_110, 0) <> 0)
        AND f_timestamp = 'CURRENT_MONTH_END'
    GROUP BY f_money_type
) AS pmm_au ON pmm.f_money_type = pmm_au.f_money_type
JOIN
(
    SELECT
        t.f_money_type,
        SUM(IFNULL(tgm.f_count_games,0)) AS TotalGames
    FROM
        t_table t
            INNER JOIN t_analytics_tables_games_monthly tgm ON t.f_id = tgm.f_table_id
    WHERE
        t.f_tournament_id = 0
        AND tgm.f_timestamp = 'CURRENT_MONTH_END'
    GROUP BY
        t.f_money_type
) AS tgm ON pmm.f_money_type = tgm.f_money_type
JOIN
(
    SELECT 
        f_money_type,
        COUNT(DISTINCT f_player_id) AS AULastMonth
    FROM t_analytics_players_money_monthly
    WHERE
        (IFNULL(f_rake_35, 0) <> 0 OR IFNULL(f_rake_54, 0) <> 0 OR IFNULL(f_rake_65, 0) <> 0 OR IFNULL(f_rake_66, 0) <> 0 OR IFNULL(f_rake_67, 0) <> 0 OR IFNULL(f_rake_68, 0) <> 0 OR IFNULL(f_rake_69, 0) <> 0 OR IFNULL(f_rake_70, 0) <> 0 OR IFNULL(f_rake_71, 0) <> 0 OR IFNULL(f_rake_72, 0) <> 0 OR IFNULL(f_rake_73, 0) <> 0 OR IFNULL(f_rake_74, 0) <> 0 OR IFNULL(f_rake_75, 0) <> 0 OR IFNULL(f_rake_76, 0) <> 0 OR IFNULL(f_rake_77, 0) <> 0 OR IFNULL(f_rake_78, 0) <> 0 OR IFNULL(f_rake_79, 0) <> 0 OR IFNULL(f_rake_80, 0) <> 0 OR IFNULL(f_rake_81, 0) <> 0 OR IFNULL(f_rake_82, 0) <> 0 OR IFNULL(f_rake_83, 0) <> 0 OR IFNULL(f_rake_84, 0) <> 0 OR IFNULL(f_rake_85, 0) <> 0 OR IFNULL(f_rake_86, 0) <> 0 OR IFNULL(f_rake_87, 0) <> 0 OR IFNULL(f_rake_88, 0) <> 0 OR IFNULL(f_rake_89, 0) <> 0 OR IFNULL(f_rake_90, 0) <> 0 OR IFNULL(f_rake_91, 0) <> 0 OR IFNULL(f_rake_92, 0) <> 0 OR IFNULL(f_rake_93, 0) <> 0 OR IFNULL(f_rake_94, 0) <> 0 OR IFNULL(f_rake_95, 0) <> 0 OR IFNULL(f_rake_96, 0) <> 0 OR IFNULL(f_rake_97, 0) <> 0 OR IFNULL(f_rake_98, 0) <> 0 OR IFNULL(f_rake_99, 0) <> 0 OR IFNULL(f_rake_34, 0) <> 0 OR IFNULL(f_rake_55, 0) <> 0 OR IFNULL(f_rake_100, 0) <> 0 OR IFNULL(f_rake_63, 0) <> 0 OR IFNULL(f_rake_64, 0) <> 0 OR IFNULL(f_rake_101, 0) <> 0 OR IFNULL(f_rake_102, 0) <> 0 OR IFNULL(f_rake_103, 0) <> 0 OR IFNULL(f_rake_104, 0) <> 0 OR IFNULL(f_rake_105, 0) <> 0 OR IFNULL(f_rake_106, 0) <> 0 OR IFNULL(f_rake_107, 0) <> 0 OR IFNULL(f_rake_108, 0) <> 0 OR IFNULL(f_rake_109, 0) <> 0 OR IFNULL(f_rake_110, 0) <> 0)
        AND f_timestamp = 'LAST_MONTH_END'
    GROUP BY f_money_type
) AS pgm_aulastmonth ON pmm.f_money_type = pgm_aulastmonth.f_money_type
JOIN
(
    SELECT 
        f_money_type,
        COUNT(DISTINCT f_player_id) AS AULastCurrent
    FROM t_analytics_players_money_monthly
    WHERE
        f_player_id IN (
            SELECT f_player_id
            FROM t_analytics_players_money_monthly
            WHERE f_timestamp = 'CURRENT_MONTH_END'
            AND (IFNULL(f_rake_35, 0) <> 0 OR IFNULL(f_rake_54, 0) <> 0 OR IFNULL(f_rake_65, 0) <> 0 OR IFNULL(f_rake_66, 0) <> 0 OR IFNULL(f_rake_67, 0) <> 0 OR IFNULL(f_rake_68, 0) <> 0 OR IFNULL(f_rake_69, 0) <> 0 OR IFNULL(f_rake_70, 0) <> 0 OR IFNULL(f_rake_71, 0) <> 0 OR IFNULL(f_rake_72, 0) <> 0 OR IFNULL(f_rake_73, 0) <> 0 OR IFNULL(f_rake_74, 0) <> 0 OR IFNULL(f_rake_75, 0) <> 0 OR IFNULL(f_rake_76, 0) <> 0 OR IFNULL(f_rake_77, 0) <> 0 OR IFNULL(f_rake_78, 0) <> 0 OR IFNULL(f_rake_79, 0) <> 0 OR IFNULL(f_rake_80, 0) <> 0 OR IFNULL(f_rake_81, 0) <> 0 OR IFNULL(f_rake_82, 0) <> 0 OR IFNULL(f_rake_83, 0) <> 0 OR IFNULL(f_rake_84, 0) <> 0 OR IFNULL(f_rake_85, 0) <> 0 OR IFNULL(f_rake_86, 0) <> 0 OR IFNULL(f_rake_87, 0) <> 0 OR IFNULL(f_rake_88, 0) <> 0 OR IFNULL(f_rake_89, 0) <> 0 OR IFNULL(f_rake_90, 0) <> 0 OR IFNULL(f_rake_91, 0) <> 0 OR IFNULL(f_rake_92, 0) <> 0 OR IFNULL(f_rake_93, 0) <> 0 OR IFNULL(f_rake_94, 0) <> 0 OR IFNULL(f_rake_95, 0) <> 0 OR IFNULL(f_rake_96, 0) <> 0 OR IFNULL(f_rake_97, 0) <> 0 OR IFNULL(f_rake_98, 0) <> 0 OR IFNULL(f_rake_99, 0) <> 0 OR IFNULL(f_rake_34, 0) <> 0 OR IFNULL(f_rake_55, 0) <> 0 OR IFNULL(f_rake_100, 0) <> 0 OR IFNULL(f_rake_63, 0) <> 0 OR IFNULL(f_rake_64, 0) <> 0 OR IFNULL(f_rake_101, 0) <> 0 OR IFNULL(f_rake_102, 0) <> 0 OR IFNULL(f_rake_103, 0) <> 0 OR IFNULL(f_rake_104, 0) <> 0 OR IFNULL(f_rake_105, 0) <> 0 OR IFNULL(f_rake_106, 0) <> 0 OR IFNULL(f_rake_107, 0) <> 0 OR IFNULL(f_rake_108, 0) <> 0 OR IFNULL(f_rake_109, 0) <> 0 OR IFNULL(f_rake_110, 0) <> 0)
        )
        AND f_player_id IN (
            SELECT f_player_id
            FROM t_analytics_players_money_monthly
            WHERE f_timestamp = 'LAST_MONTH_END'
            AND (IFNULL(f_rake_35, 0) <> 0 OR IFNULL(f_rake_54, 0) <> 0 OR IFNULL(f_rake_65, 0) <> 0 OR IFNULL(f_rake_66, 0) <> 0 OR IFNULL(f_rake_67, 0) <> 0 OR IFNULL(f_rake_68, 0) <> 0 OR IFNULL(f_rake_69, 0) <> 0 OR IFNULL(f_rake_70, 0) <> 0 OR IFNULL(f_rake_71, 0) <> 0 OR IFNULL(f_rake_72, 0) <> 0 OR IFNULL(f_rake_73, 0) <> 0 OR IFNULL(f_rake_74, 0) <> 0 OR IFNULL(f_rake_75, 0) <> 0 OR IFNULL(f_rake_76, 0) <> 0 OR IFNULL(f_rake_77, 0) <> 0 OR IFNULL(f_rake_78, 0) <> 0 OR IFNULL(f_rake_79, 0) <> 0 OR IFNULL(f_rake_80, 0) <> 0 OR IFNULL(f_rake_81, 0) <> 0 OR IFNULL(f_rake_82, 0) <> 0 OR IFNULL(f_rake_83, 0) <> 0 OR IFNULL(f_rake_84, 0) <> 0 OR IFNULL(f_rake_85, 0) <> 0 OR IFNULL(f_rake_86, 0) <> 0 OR IFNULL(f_rake_87, 0) <> 0 OR IFNULL(f_rake_88, 0) <> 0 OR IFNULL(f_rake_89, 0) <> 0 OR IFNULL(f_rake_90, 0) <> 0 OR IFNULL(f_rake_91, 0) <> 0 OR IFNULL(f_rake_92, 0) <> 0 OR IFNULL(f_rake_93, 0) <> 0 OR IFNULL(f_rake_94, 0) <> 0 OR IFNULL(f_rake_95, 0) <> 0 OR IFNULL(f_rake_96, 0) <> 0 OR IFNULL(f_rake_97, 0) <> 0 OR IFNULL(f_rake_98, 0) <> 0 OR IFNULL(f_rake_99, 0) <> 0 OR IFNULL(f_rake_34, 0) <> 0 OR IFNULL(f_rake_55, 0) <> 0 OR IFNULL(f_rake_100, 0) <> 0 OR IFNULL(f_rake_63, 0) <> 0 OR IFNULL(f_rake_64, 0) <> 0 OR IFNULL(f_rake_101, 0) <> 0 OR IFNULL(f_rake_102, 0) <> 0 OR IFNULL(f_rake_103, 0) <> 0 OR IFNULL(f_rake_104, 0) <> 0 OR IFNULL(f_rake_105, 0) <> 0 OR IFNULL(f_rake_106, 0) <> 0 OR IFNULL(f_rake_107, 0) <> 0 OR IFNULL(f_rake_108, 0) <> 0 OR IFNULL(f_rake_109, 0) <> 0 OR IFNULL(f_rake_110, 0) <> 0)
        )
    GROUP BY f_money_type
) AS pgm_aulastcurrent ON pmm.f_money_type = pgm_aulastcurrent.f_money_type
```

>**3) Отчет по кэш играм с разбивкой по типам игр**

```sql
SELECT 
    r.GameType,
    r.CurrencyName AS 'Currency',
    r.TotalRake,
    r.TotalGameCount,
    IFNULL(a.AU, 0) AS AU,
    IFNULL(n.NewAU, 0) AS NewAU,
    IFNULL(lm.AULastMonth, 0) AS AULastMonth,
    IFNULL(lc.AULastCurrent, 0) AS AULastCurrent
FROM 
    (
        SELECT 
            CASE atgm.f_game_type
                WHEN 0 THEN 'Unknown'
                WHEN 34 THEN 'CUSTOM'
                WHEN 35 THEN 'MIXED'
                WHEN 54 THEN 'SIXPLUSHOLDEM'
                WHEN 55 THEN 'TEENPATTI'
                WHEN 63 THEN 'RUMMYOKEY'
                WHEN 64 THEN 'RUMMYOKEYPOOL'
                WHEN 65 THEN 'RUMMYPOINTS'
                WHEN 66 THEN 'BADUGI'
                WHEN 67 THEN 'BADACEY'
                WHEN 68 THEN '27TRIPLEDRAW'
                WHEN 69 THEN 'BADEUCY'
                WHEN 70 THEN 'CHINESEOF'
                WHEN 71 THEN 'OMAHA5HL'
                WHEN 72 THEN 'HOLDEM'
                WHEN 73 THEN 'CHINESEOFPINEAPPLE'
                WHEN 74 THEN 'PINEAPPLEHOLDEM'
                WHEN 75 THEN 'TURKISH'
                WHEN 76 THEN 'CHINESEOF27PINEAPPLE'
                WHEN 77 THEN 'CHINESEOFPROGRPINEAPPLE'
                WHEN 78 THEN 'CHINESE'
                WHEN 79 THEN 'OMAHA'
                WHEN 80 THEN 'OMAHAHL'
                WHEN 81 THEN '7ADRAWHOLDEM'
                WHEN 82 THEN 'RAZZ'
                WHEN 83 THEN 'STUD'
                WHEN 84 THEN 'STUDHL'
                WHEN 85 THEN 'CHINESEOFTURBO'
                WHEN 86 THEN 'RUMMYDEALS'
                WHEN 87 THEN 'RUMMYPOOL'
                WHEN 88 THEN 'OMAHA5'
                WHEN 89 THEN 'COURCHEVEL'
                WHEN 90 THEN 'TRITONHOLDEM'
                WHEN 91 THEN 'OMAHA6'
                WHEN 92 THEN 'TELESINA'
                WHEN 93 THEN 'OMAHA6HL'
                WHEN 94 THEN '27SINGLEDRAW'
                WHEN 95 THEN 'TELESINAWITHVELA'
                WHEN 96 THEN '7ATELESINA'
                WHEN 97 THEN '7ATELESINAWITHVELA'
                WHEN 98 THEN 'CALLBREAK'
                WHEN 99 THEN 'BIG2'
                WHEN 100 THEN 'BIG2POOL'
                WHEN 101 THEN 'COWBOY'
                WHEN 102 THEN 'CHINESEOFULTIMATE'
                WHEN 103 THEN 'CHINESEOFJOKERS'
                WHEN 104 THEN 'CHINESEOFJOKERSULTIMATE'
                ELSE CAST(atgm.f_game_type AS CHAR)
            END AS GameType,
            atgm.f_money_type AS Currency,
            c.f_iso_code AS CurrencyName,
            ROUND(SUM(IFNULL(atgm.f_rake, 0)) / POW(10, c.f_precision), c.f_precision) AS TotalRake,
            SUM(atgm.f_count_games) AS TotalGameCount
        FROM t_analytics_tables_games_monthly atgm
        LEFT JOIN t_table t ON t.f_id = atgm.f_table_id
        INNER JOIN t_currency c ON c.f_money_type = atgm.f_money_type
        WHERE atgm.f_timestamp = 'CURRENT_MONTH_END'
        GROUP BY atgm.f_game_type, atgm.f_money_type
    ) r
LEFT JOIN (
    SELECT 
        GameType,
        f_money_type AS Currency,
        COUNT(DISTINCT f_player_id) AS AU
    FROM 
        t_analytics_players_money_monthly apmm
    JOIN (
        SELECT 0 AS game_type, 'Unknown' AS GameType UNION ALL
        SELECT 34, 'CUSTOM' UNION ALL
        SELECT 35, 'MIXED' UNION ALL
        SELECT 54, 'SIXPLUSHOLDEM' UNION ALL
        SELECT 55, 'TEENPATTI' UNION ALL
        SELECT 63, 'RUMMYOKEY' UNION ALL
        SELECT 64, 'RUMMYOKEYPOOL' UNION ALL
        SELECT 65, 'RUMMYPOINTS' UNION ALL
        SELECT 66, 'BADUGI' UNION ALL
        SELECT 67, 'BADACEY' UNION ALL
        SELECT 68, '27TRIPLEDRAW' UNION ALL
        SELECT 69, 'BADEUCY' UNION ALL
        SELECT 70, 'CHINESEOF' UNION ALL
        SELECT 71, 'OMAHA5HL' UNION ALL
        SELECT 72, 'HOLDEM' UNION ALL
        SELECT 73, 'CHINESEOFPINEAPPLE' UNION ALL
        SELECT 74, 'PINEAPPLEHOLDEM' UNION ALL
        SELECT 75, 'TURKISH' UNION ALL
        SELECT 76, 'CHINESEOF27PINEAPPLE' UNION ALL
        SELECT 77, 'CHINESEOFPROGRPINEAPPLE' UNION ALL
        SELECT 78, 'CHINESE' UNION ALL
        SELECT 79, 'OMAHA' UNION ALL
        SELECT 80, 'OMAHAHL' UNION ALL
        SELECT 81, '7ADRAWHOLDEM' UNION ALL
        SELECT 82, 'RAZZ' UNION ALL
        SELECT 83, 'STUD' UNION ALL
        SELECT 84, 'STUDHL' UNION ALL
        SELECT 85, 'CHINESEOFTURBO' UNION ALL
        SELECT 86, 'RUMMYDEALS' UNION ALL
        SELECT 87, 'RUMMYPOOL' UNION ALL
        SELECT 88, 'OMAHA5' UNION ALL
        SELECT 89, 'COURCHEVEL' UNION ALL
        SELECT 90, 'TRITONHOLDEM' UNION ALL
        SELECT 91, 'OMAHA6' UNION ALL
        SELECT 92, 'TELESINA' UNION ALL
        SELECT 93, 'OMAHA6HL' UNION ALL
        SELECT 94, '27SINGLEDRAW' UNION ALL
        SELECT 95, 'TELESINAWITHVELA' UNION ALL
        SELECT 96, '7ATELESINA' UNION ALL
        SELECT 97, '7ATELESINAWITHVELA' UNION ALL
        SELECT 98, 'CALLBREAK' UNION ALL
        SELECT 99, 'BIG2' UNION ALL
        SELECT 100, 'BIG2POOL' UNION ALL
        SELECT 101, 'COWBOY' UNION ALL
        SELECT 102, 'CHINESEOFULTIMATE' UNION ALL
        SELECT 103, 'CHINESEOFJOKERS' UNION ALL
        SELECT 104, 'CHINESEOFJOKERSULTIMATE'
    ) gt ON 1=1
    WHERE
        (
            (gt.game_type = 34 AND IFNULL(apmm.f_rake_34, 0) <> 0) OR
            (gt.game_type = 35 AND IFNULL(apmm.f_rake_35, 0) <> 0) OR
            (gt.game_type = 54 AND IFNULL(apmm.f_rake_54, 0) <> 0) OR
            (gt.game_type = 55 AND IFNULL(apmm.f_rake_55, 0) <> 0) OR
            (gt.game_type = 63 AND IFNULL(apmm.f_rake_63, 0) <> 0) OR
            (gt.game_type = 64 AND IFNULL(apmm.f_rake_64, 0) <> 0) OR
            (gt.game_type = 65 AND IFNULL(apmm.f_rake_65, 0) <> 0) OR
            (gt.game_type = 66 AND IFNULL(apmm.f_rake_66, 0) <> 0) OR
            (gt.game_type = 67 AND IFNULL(apmm.f_rake_67, 0) <> 0) OR
            (gt.game_type = 68 AND IFNULL(apmm.f_rake_68, 0) <> 0) OR
            (gt.game_type = 69 AND IFNULL(apmm.f_rake_69, 0) <> 0) OR
            (gt.game_type = 70 AND IFNULL(apmm.f_rake_70, 0) <> 0) OR
            (gt.game_type = 71 AND IFNULL(apmm.f_rake_71, 0) <> 0) OR
            (gt.game_type = 72 AND IFNULL(apmm.f_rake_72, 0) <> 0) OR
            (gt.game_type = 73 AND IFNULL(apmm.f_rake_73, 0) <> 0) OR
            (gt.game_type = 74 AND IFNULL(apmm.f_rake_74, 0) <> 0) OR
            (gt.game_type = 75 AND IFNULL(apmm.f_rake_75, 0) <> 0) OR
            (gt.game_type = 76 AND IFNULL(apmm.f_rake_76, 0) <> 0) OR
            (gt.game_type = 77 AND IFNULL(apmm.f_rake_77, 0) <> 0) OR
            (gt.game_type = 78 AND IFNULL(apmm.f_rake_78, 0) <> 0) OR
            (gt.game_type = 79 AND IFNULL(apmm.f_rake_79, 0) <> 0) OR
            (gt.game_type = 80 AND IFNULL(apmm.f_rake_80, 0) <> 0) OR
            (gt.game_type = 81 AND IFNULL(apmm.f_rake_81, 0) <> 0) OR
            (gt.game_type = 82 AND IFNULL(apmm.f_rake_82, 0) <> 0) OR
            (gt.game_type = 83 AND IFNULL(apmm.f_rake_83, 0) <> 0) OR
            (gt.game_type = 84 AND IFNULL(apmm.f_rake_84, 0) <> 0) OR
            (gt.game_type = 85 AND IFNULL(apmm.f_rake_85, 0) <> 0) OR
            (gt.game_type = 86 AND IFNULL(apmm.f_rake_86, 0) <> 0) OR
            (gt.game_type = 87 AND IFNULL(apmm.f_rake_87, 0) <> 0) OR
            (gt.game_type = 88 AND IFNULL(apmm.f_rake_88, 0) <> 0) OR
            (gt.game_type = 89 AND IFNULL(apmm.f_rake_89, 0) <> 0) OR
            (gt.game_type = 90 AND IFNULL(apmm.f_rake_90, 0) <> 0) OR
            (gt.game_type = 91 AND IFNULL(apmm.f_rake_91, 0) <> 0) OR
            (gt.game_type = 92 AND IFNULL(apmm.f_rake_92, 0) <> 0) OR
            (gt.game_type = 93 AND IFNULL(apmm.f_rake_93, 0) <> 0) OR
            (gt.game_type = 94 AND IFNULL(apmm.f_rake_94, 0) <> 0) OR
            (gt.game_type = 95 AND IFNULL(apmm.f_rake_95, 0) <> 0) OR
            (gt.game_type = 96 AND IFNULL(apmm.f_rake_96, 0) <> 0) OR
            (gt.game_type = 97 AND IFNULL(apmm.f_rake_97, 0) <> 0) OR
            (gt.game_type = 98 AND IFNULL(apmm.f_rake_98, 0) <> 0) OR
            (gt.game_type = 99 AND IFNULL(apmm.f_rake_99, 0) <> 0) OR
            (gt.game_type = 100 AND IFNULL(apmm.f_rake_100, 0) <> 0) OR
            (gt.game_type = 101 AND IFNULL(apmm.f_rake_101, 0) <> 0) OR
            (gt.game_type = 102 AND IFNULL(apmm.f_rake_102, 0) <> 0) OR
            (gt.game_type = 103 AND IFNULL(apmm.f_rake_103, 0) <> 0) OR
            (gt.game_type = 104 AND IFNULL(apmm.f_rake_104, 0) <> 0)
        )
        AND apmm.f_timestamp = 'CURRENT_MONTH_END'
    GROUP BY gt.GameType, apmm.f_money_type
) a ON r.GameType = a.GameType AND r.Currency = a.Currency
LEFT JOIN (
    SELECT 
        GameType,
        f_money_type AS Currency,
        COUNT(DISTINCT f_player_id) AS NewAU
    FROM 
        t_analytics_players_money_monthly apmm
    JOIN (
        SELECT 0 AS game_type, 'Unknown' AS GameType UNION ALL
        SELECT 34, 'CUSTOM' UNION ALL
        SELECT 35, 'MIXED' UNION ALL
        SELECT 54, 'SIXPLUSHOLDEM' UNION ALL
        SELECT 55, 'TEENPATTI' UNION ALL
        SELECT 63, 'RUMMYOKEY' UNION ALL
        SELECT 64, 'RUMMYOKEYPOOL' UNION ALL
        SELECT 65, 'RUMMYPOINTS' UNION ALL
        SELECT 66, 'BADUGI' UNION ALL
        SELECT 67, 'BADACEY' UNION ALL
        SELECT 68, '27TRIPLEDRAW' UNION ALL
        SELECT 69, 'BADEUCY' UNION ALL
        SELECT 70, 'CHINESEOF' UNION ALL
        SELECT 71, 'OMAHA5HL' UNION ALL
        SELECT 72, 'HOLDEM' UNION ALL
        SELECT 73, 'CHINESEOFPINEAPPLE' UNION ALL
        SELECT 74, 'PINEAPPLEHOLDEM' UNION ALL
        SELECT 75, 'TURKISH' UNION ALL
        SELECT 76, 'CHINESEOF27PINEAPPLE' UNION ALL
        SELECT 77, 'CHINESEOFPROGRPINEAPPLE' UNION ALL
        SELECT 78, 'CHINESE' UNION ALL
        SELECT 79, 'OMAHA' UNION ALL
        SELECT 80, 'OMAHAHL' UNION ALL
        SELECT 81, '7ADRAWHOLDEM' UNION ALL
        SELECT 82, 'RAZZ' UNION ALL
        SELECT 83, 'STUD' UNION ALL
        SELECT 84, 'STUDHL' UNION ALL
        SELECT 85, 'CHINESEOFTURBO' UNION ALL
        SELECT 86, 'RUMMYDEALS' UNION ALL
        SELECT 87, 'RUMMYPOOL' UNION ALL
        SELECT 88, 'OMAHA5' UNION ALL
        SELECT 89, 'COURCHEVEL' UNION ALL
        SELECT 90, 'TRITONHOLDEM' UNION ALL
        SELECT 91, 'OMAHA6' UNION ALL
        SELECT 92, 'TELESINA' UNION ALL
        SELECT 93, 'OMAHA6HL' UNION ALL
        SELECT 94, '27SINGLEDRAW' UNION ALL
        SELECT 95, 'TELESINAWITHVELA' UNION ALL
        SELECT 96, '7ATELESINA' UNION ALL
        SELECT 97, '7ATELESINAWITHVELA' UNION ALL
        SELECT 98, 'CALLBREAK' UNION ALL
        SELECT 99, 'BIG2' UNION ALL
        SELECT 100, 'BIG2POOL' UNION ALL
        SELECT 101, 'COWBOY' UNION ALL
        SELECT 102, 'CHINESEOFULTIMATE' UNION ALL
        SELECT 103, 'CHINESEOFJOKERS' UNION ALL
        SELECT 104, 'CHINESEOFJOKERSULTIMATE'
    ) gt ON 1=1
    WHERE
        (
            (gt.game_type = 34 AND IFNULL(apmm.f_rake_34, 0) <> 0) OR
            (gt.game_type = 35 AND IFNULL(apmm.f_rake_35, 0) <> 0) OR
            (gt.game_type = 54 AND IFNULL(apmm.f_rake_54, 0) <> 0) OR
            (gt.game_type = 55 AND IFNULL(apmm.f_rake_55, 0) <> 0) OR
            (gt.game_type = 63 AND IFNULL(apmm.f_rake_63, 0) <> 0) OR
            (gt.game_type = 64 AND IFNULL(apmm.f_rake_64, 0) <> 0) OR
            (gt.game_type = 65 AND IFNULL(apmm.f_rake_65, 0) <> 0) OR
            (gt.game_type = 66 AND IFNULL(apmm.f_rake_66, 0) <> 0) OR
            (gt.game_type = 67 AND IFNULL(apmm.f_rake_67, 0) <> 0) OR
            (gt.game_type = 68 AND IFNULL(apmm.f_rake_68, 0) <> 0) OR
            (gt.game_type = 69 AND IFNULL(apmm.f_rake_69, 0) <> 0) OR
            (gt.game_type = 70 AND IFNULL(apmm.f_rake_70, 0) <> 0) OR
            (gt.game_type = 71 AND IFNULL(apmm.f_rake_71, 0) <> 0) OR
            (gt.game_type = 72 AND IFNULL(apmm.f_rake_72, 0) <> 0) OR
            (gt.game_type = 73 AND IFNULL(apmm.f_rake_73, 0) <> 0) OR
            (gt.game_type = 74 AND IFNULL(apmm.f_rake_74, 0) <> 0) OR
            (gt.game_type = 75 AND IFNULL(apmm.f_rake_75, 0) <> 0) OR
            (gt.game_type = 76 AND IFNULL(apmm.f_rake_76, 0) <> 0) OR
            (gt.game_type = 77 AND IFNULL(apmm.f_rake_77, 0) <> 0) OR
            (gt.game_type = 78 AND IFNULL(apmm.f_rake_78, 0) <> 0) OR
            (gt.game_type = 79 AND IFNULL(apmm.f_rake_79, 0) <> 0) OR
            (gt.game_type = 80 AND IFNULL(apmm.f_rake_80, 0) <> 0) OR
            (gt.game_type = 81 AND IFNULL(apmm.f_rake_81, 0) <> 0) OR
            (gt.game_type = 82 AND IFNULL(apmm.f_rake_82, 0) <> 0) OR
            (gt.game_type = 83 AND IFNULL(apmm.f_rake_83, 0) <> 0) OR
            (gt.game_type = 84 AND IFNULL(apmm.f_rake_84, 0) <> 0) OR
            (gt.game_type = 85 AND IFNULL(apmm.f_rake_85, 0) <> 0) OR
            (gt.game_type = 86 AND IFNULL(apmm.f_rake_86, 0) <> 0) OR
            (gt.game_type = 87 AND IFNULL(apmm.f_rake_87, 0) <> 0) OR
            (gt.game_type = 88 AND IFNULL(apmm.f_rake_88, 0) <> 0) OR
            (gt.game_type = 89 AND IFNULL(apmm.f_rake_89, 0) <> 0) OR
            (gt.game_type = 90 AND IFNULL(apmm.f_rake_90, 0) <> 0) OR
            (gt.game_type = 91 AND IFNULL(apmm.f_rake_91, 0) <> 0) OR
            (gt.game_type = 92 AND IFNULL(apmm.f_rake_92, 0) <> 0) OR
            (gt.game_type = 93 AND IFNULL(apmm.f_rake_93, 0) <> 0) OR
            (gt.game_type = 94 AND IFNULL(apmm.f_rake_94, 0) <> 0) OR
            (gt.game_type = 95 AND IFNULL(apmm.f_rake_95, 0) <> 0) OR
            (gt.game_type = 96 AND IFNULL(apmm.f_rake_96, 0) <> 0) OR
            (gt.game_type = 97 AND IFNULL(apmm.f_rake_97, 0) <> 0) OR
            (gt.game_type = 98 AND IFNULL(apmm.f_rake_98, 0) <> 0) OR
            (gt.game_type = 99 AND IFNULL(apmm.f_rake_99, 0) <> 0) OR
            (gt.game_type = 100 AND IFNULL(apmm.f_rake_100, 0) <> 0) OR
            (gt.game_type = 101 AND IFNULL(apmm.f_rake_101, 0) <> 0) OR
            (gt.game_type = 102 AND IFNULL(apmm.f_rake_102, 0) <> 0) OR
            (gt.game_type = 103 AND IFNULL(apmm.f_rake_103, 0) <> 0) OR
            (gt.game_type = 104 AND IFNULL(apmm.f_rake_104, 0) <> 0)
        )
        AND apmm.f_timestamp = 'CURRENT_MONTH_END'
        AND apmm.f_player_id IN (
            SELECT f_id FROM t_player 
            WHERE f_register_stamp BETWEEN 'FIRST_DAY_CURRENT' AND 'CURRENT_MONTH_END'
        )
    GROUP BY gt.GameType, apmm.f_money_type
) n ON r.GameType = n.GameType AND r.Currency = n.Currency
LEFT JOIN (
    SELECT 
        GameType,
        f_money_type AS Currency,
        COUNT(DISTINCT f_player_id) AS AULastMonth
    FROM 
        t_analytics_players_money_monthly apmm
    JOIN (
        SELECT 0 AS game_type, 'Unknown' AS GameType UNION ALL
        SELECT 34, 'CUSTOM' UNION ALL
        SELECT 35, 'MIXED' UNION ALL
        SELECT 54, 'SIXPLUSHOLDEM' UNION ALL
        SELECT 55, 'TEENPATTI' UNION ALL
        SELECT 63, 'RUMMYOKEY' UNION ALL
        SELECT 64, 'RUMMYOKEYPOOL' UNION ALL
        SELECT 65, 'RUMMYPOINTS' UNION ALL
        SELECT 66, 'BADUGI' UNION ALL
        SELECT 67, 'BADACEY' UNION ALL
        SELECT 68, '27TRIPLEDRAW' UNION ALL
        SELECT 69, 'BADEUCY' UNION ALL
        SELECT 70, 'CHINESEOF' UNION ALL
        SELECT 71, 'OMAHA5HL' UNION ALL
        SELECT 72, 'HOLDEM' UNION ALL
        SELECT 73, 'CHINESEOFPINEAPPLE' UNION ALL
        SELECT 74, 'PINEAPPLEHOLDEM' UNION ALL
        SELECT 75, 'TURKISH' UNION ALL
        SELECT 76, 'CHINESEOF27PINEAPPLE' UNION ALL
        SELECT 77, 'CHINESEOFPROGRPINEAPPLE' UNION ALL
        SELECT 78, 'CHINESE' UNION ALL
        SELECT 79, 'OMAHA' UNION ALL
        SELECT 80, 'OMAHAHL' UNION ALL
        SELECT 81, '7ADRAWHOLDEM' UNION ALL
        SELECT 82, 'RAZZ' UNION ALL
        SELECT 83, 'STUD' UNION ALL
        SELECT 84, 'STUDHL' UNION ALL
        SELECT 85, 'CHINESEOFTURBO' UNION ALL
        SELECT 86, 'RUMMYDEALS' UNION ALL
        SELECT 87, 'RUMMYPOOL' UNION ALL
        SELECT 88, 'OMAHA5' UNION ALL
        SELECT 89, 'COURCHEVEL' UNION ALL
        SELECT 90, 'TRITONHOLDEM' UNION ALL
        SELECT 91, 'OMAHA6' UNION ALL
        SELECT 92, 'TELESINA' UNION ALL
        SELECT 93, 'OMAHA6HL' UNION ALL
        SELECT 94, '27SINGLEDRAW' UNION ALL
        SELECT 95, 'TELESINAWITHVELA' UNION ALL
        SELECT 96, '7ATELESINA' UNION ALL
        SELECT 97, '7ATELESINAWITHVELA' UNION ALL
        SELECT 98, 'CALLBREAK' UNION ALL
        SELECT 99, 'BIG2' UNION ALL
        SELECT 100, 'BIG2POOL' UNION ALL
        SELECT 101, 'COWBOY' UNION ALL
        SELECT 102, 'CHINESEOFULTIMATE' UNION ALL
        SELECT 103, 'CHINESEOFJOKERS' UNION ALL
        SELECT 104, 'CHINESEOFJOKERSULTIMATE'
    ) gt ON 1=1
    WHERE
        (
            (gt.game_type = 34 AND IFNULL(apmm.f_rake_34, 0) <> 0) OR
            (gt.game_type = 35 AND IFNULL(apmm.f_rake_35, 0) <> 0) OR
            (gt.game_type = 54 AND IFNULL(apmm.f_rake_54, 0) <> 0) OR
            (gt.game_type = 55 AND IFNULL(apmm.f_rake_55, 0) <> 0) OR
            (gt.game_type = 63 AND IFNULL(apmm.f_rake_63, 0) <> 0) OR
            (gt.game_type = 64 AND IFNULL(apmm.f_rake_64, 0) <> 0) OR
            (gt.game_type = 65 AND IFNULL(apmm.f_rake_65, 0) <> 0) OR
            (gt.game_type = 66 AND IFNULL(apmm.f_rake_66, 0) <> 0) OR
            (gt.game_type = 67 AND IFNULL(apmm.f_rake_67, 0) <> 0) OR
            (gt.game_type = 68 AND IFNULL(apmm.f_rake_68, 0) <> 0) OR
            (gt.game_type = 69 AND IFNULL(apmm.f_rake_69, 0) <> 0) OR
            (gt.game_type = 70 AND IFNULL(apmm.f_rake_70, 0) <> 0) OR
            (gt.game_type = 71 AND IFNULL(apmm.f_rake_71, 0) <> 0) OR
            (gt.game_type = 72 AND IFNULL(apmm.f_rake_72, 0) <> 0) OR
            (gt.game_type = 73 AND IFNULL(apmm.f_rake_73, 0) <> 0) OR
            (gt.game_type = 74 AND IFNULL(apmm.f_rake_74, 0) <> 0) OR
            (gt.game_type = 75 AND IFNULL(apmm.f_rake_75, 0) <> 0) OR
            (gt.game_type = 76 AND IFNULL(apmm.f_rake_76, 0) <> 0) OR
            (gt.game_type = 77 AND IFNULL(apmm.f_rake_77, 0) <> 0) OR
            (gt.game_type = 78 AND IFNULL(apmm.f_rake_78, 0) <> 0) OR
            (gt.game_type = 79 AND IFNULL(apmm.f_rake_79, 0) <> 0) OR
            (gt.game_type = 80 AND IFNULL(apmm.f_rake_80, 0) <> 0) OR
            (gt.game_type = 81 AND IFNULL(apmm.f_rake_81, 0) <> 0) OR
            (gt.game_type = 82 AND IFNULL(apmm.f_rake_82, 0) <> 0) OR
            (gt.game_type = 83 AND IFNULL(apmm.f_rake_83, 0) <> 0) OR
            (gt.game_type = 84 AND IFNULL(apmm.f_rake_84, 0) <> 0) OR
            (gt.game_type = 85 AND IFNULL(apmm.f_rake_85, 0) <> 0) OR
            (gt.game_type = 86 AND IFNULL(apmm.f_rake_86, 0) <> 0) OR
            (gt.game_type = 87 AND IFNULL(apmm.f_rake_87, 0) <> 0) OR
            (gt.game_type = 88 AND IFNULL(apmm.f_rake_88, 0) <> 0) OR
            (gt.game_type = 89 AND IFNULL(apmm.f_rake_89, 0) <> 0) OR
            (gt.game_type = 90 AND IFNULL(apmm.f_rake_90, 0) <> 0) OR
            (gt.game_type = 91 AND IFNULL(apmm.f_rake_91, 0) <> 0) OR
            (gt.game_type = 92 AND IFNULL(apmm.f_rake_92, 0) <> 0) OR
            (gt.game_type = 93 AND IFNULL(apmm.f_rake_93, 0) <> 0) OR
            (gt.game_type = 94 AND IFNULL(apmm.f_rake_94, 0) <> 0) OR
            (gt.game_type = 95 AND IFNULL(apmm.f_rake_95, 0) <> 0) OR
            (gt.game_type = 96 AND IFNULL(apmm.f_rake_96, 0) <> 0) OR
            (gt.game_type = 97 AND IFNULL(apmm.f_rake_97, 0) <> 0) OR
            (gt.game_type = 98 AND IFNULL(apmm.f_rake_98, 0) <> 0) OR
            (gt.game_type = 99 AND IFNULL(apmm.f_rake_99, 0) <> 0) OR
            (gt.game_type = 100 AND IFNULL(apmm.f_rake_100, 0) <> 0) OR
            (gt.game_type = 101 AND IFNULL(apmm.f_rake_101, 0) <> 0) OR
            (gt.game_type = 102 AND IFNULL(apmm.f_rake_102, 0) <> 0) OR
            (gt.game_type = 103 AND IFNULL(apmm.f_rake_103, 0) <> 0) OR
            (gt.game_type = 104 AND IFNULL(apmm.f_rake_104, 0) <> 0)
        )
        AND apmm.f_timestamp = 'LAST_MONTH_END'
    GROUP BY gt.GameType, apmm.f_money_type
) lm ON r.GameType = lm.GameType AND r.Currency = lm.Currency
LEFT JOIN (
    SELECT 
        gt.GameType,
        apmm.f_money_type AS Currency,
        COUNT(DISTINCT apmm.f_player_id) AS AULastCurrent
    FROM 
        t_analytics_players_money_monthly apmm
    JOIN (
        SELECT 0 AS game_type, 'Unknown' AS GameType UNION ALL
        SELECT 34, 'CUSTOM' UNION ALL
        SELECT 35, 'MIXED' UNION ALL
        SELECT 54, 'SIXPLUSHOLDEM' UNION ALL
        SELECT 55, 'TEENPATTI' UNION ALL
        SELECT 63, 'RUMMYOKEY' UNION ALL
        SELECT 64, 'RUMMYOKEYPOOL' UNION ALL
        SELECT 65, 'RUMMYPOINTS' UNION ALL
        SELECT 66, 'BADUGI' UNION ALL
        SELECT 67, 'BADACEY' UNION ALL
        SELECT 68, '27TRIPLEDRAW' UNION ALL
        SELECT 69, 'BADEUCY' UNION ALL
        SELECT 70, 'CHINESEOF' UNION ALL
        SELECT 71, 'OMAHA5HL' UNION ALL
        SELECT 72, 'HOLDEM' UNION ALL
        SELECT 73, 'CHINESEOFPINEAPPLE' UNION ALL
        SELECT 74, 'PINEAPPLEHOLDEM' UNION ALL
        SELECT 75, 'TURKISH' UNION ALL
        SELECT 76, 'CHINESEOF27PINEAPPLE' UNION ALL
        SELECT 77, 'CHINESEOFPROGRPINEAPPLE' UNION ALL
        SELECT 78, 'CHINESE' UNION ALL
        SELECT 79, 'OMAHA' UNION ALL
        SELECT 80, 'OMAHAHL' UNION ALL
        SELECT 81, '7ADRAWHOLDEM' UNION ALL
        SELECT 82, 'RAZZ' UNION ALL
        SELECT 83, 'STUD' UNION ALL
        SELECT 84, 'STUDHL' UNION ALL
        SELECT 85, 'CHINESEOFTURBO' UNION ALL
        SELECT 86, 'RUMMYDEALS' UNION ALL
        SELECT 87, 'RUMMYPOOL' UNION ALL
        SELECT 88, 'OMAHA5' UNION ALL
        SELECT 89, 'COURCHEVEL' UNION ALL
        SELECT 90, 'TRITONHOLDEM' UNION ALL
        SELECT 91, 'OMAHA6' UNION ALL
        SELECT 92, 'TELESINA' UNION ALL
        SELECT 93, 'OMAHA6HL' UNION ALL
        SELECT 94, '27SINGLEDRAW' UNION ALL
        SELECT 95, 'TELESINAWITHVELA' UNION ALL
        SELECT 96, '7ATELESINA' UNION ALL
        SELECT 97, '7ATELESINAWITHVELA' UNION ALL
        SELECT 98, 'CALLBREAK' UNION ALL
        SELECT 99, 'BIG2' UNION ALL
        SELECT 100, 'BIG2POOL' UNION ALL
        SELECT 101, 'COWBOY' UNION ALL
        SELECT 102, 'CHINESEOFULTIMATE' UNION ALL
        SELECT 103, 'CHINESEOFJOKERS' UNION ALL
        SELECT 104, 'CHINESEOFJOKERSULTIMATE'
    ) gt ON 1=1
    WHERE
        apmm.f_player_id IN (
            SELECT f_player_id
            FROM t_analytics_players_money_monthly apmm2
            WHERE apmm2.f_timestamp = 'CURRENT_MONTH_END'
            AND apmm2.f_money_type = apmm.f_money_type
            AND (
                (gt.game_type = 34 AND IFNULL(apmm2.f_rake_34, 0) <> 0) OR
                (gt.game_type = 35 AND IFNULL(apmm2.f_rake_35, 0) <> 0) OR
                (gt.game_type = 54 AND IFNULL(apmm2.f_rake_54, 0) <> 0) OR
                (gt.game_type = 55 AND IFNULL(apmm2.f_rake_55, 0) <> 0) OR
                (gt.game_type = 63 AND IFNULL(apmm2.f_rake_63, 0) <> 0) OR
                (gt.game_type = 64 AND IFNULL(apmm2.f_rake_64, 0) <> 0) OR
                (gt.game_type = 65 AND IFNULL(apmm2.f_rake_65, 0) <> 0) OR
                (gt.game_type = 66 AND IFNULL(apmm2.f_rake_66, 0) <> 0) OR
                (gt.game_type = 67 AND IFNULL(apmm2.f_rake_67, 0) <> 0) OR
                (gt.game_type = 68 AND IFNULL(apmm2.f_rake_68, 0) <> 0) OR
                (gt.game_type = 69 AND IFNULL(apmm2.f_rake_69, 0) <> 0) OR
                (gt.game_type = 70 AND IFNULL(apmm2.f_rake_70, 0) <> 0) OR
                (gt.game_type = 71 AND IFNULL(apmm2.f_rake_71, 0) <> 0) OR
                (gt.game_type = 72 AND IFNULL(apmm2.f_rake_72, 0) <> 0) OR
                (gt.game_type = 73 AND IFNULL(apmm2.f_rake_73, 0) <> 0) OR
                (gt.game_type = 74 AND IFNULL(apmm2.f_rake_74, 0) <> 0) OR
                (gt.game_type = 75 AND IFNULL(apmm2.f_rake_75, 0) <> 0) OR
                (gt.game_type = 76 AND IFNULL(apmm2.f_rake_76, 0) <> 0) OR
                (gt.game_type = 77 AND IFNULL(apmm2.f_rake_77, 0) <> 0) OR
                (gt.game_type = 78 AND IFNULL(apmm2.f_rake_78, 0) <> 0) OR
                (gt.game_type = 79 AND IFNULL(apmm2.f_rake_79, 0) <> 0) OR
                (gt.game_type = 80 AND IFNULL(apmm2.f_rake_80, 0) <> 0) OR
                (gt.game_type = 81 AND IFNULL(apmm2.f_rake_81, 0) <> 0) OR
                (gt.game_type = 82 AND IFNULL(apmm2.f_rake_82, 0) <> 0) OR
                (gt.game_type = 83 AND IFNULL(apmm2.f_rake_83, 0) <> 0) OR
                (gt.game_type = 84 AND IFNULL(apmm2.f_rake_84, 0) <> 0) OR
                (gt.game_type = 85 AND IFNULL(apmm2.f_rake_85, 0) <> 0) OR
                (gt.game_type = 86 AND IFNULL(apmm2.f_rake_86, 0) <> 0) OR
                (gt.game_type = 87 AND IFNULL(apmm2.f_rake_87, 0) <> 0) OR
                (gt.game_type = 88 AND IFNULL(apmm2.f_rake_88, 0) <> 0) OR
                (gt.game_type = 89 AND IFNULL(apmm2.f_rake_89, 0) <> 0) OR
                (gt.game_type = 90 AND IFNULL(apmm2.f_rake_90, 0) <> 0) OR
                (gt.game_type = 91 AND IFNULL(apmm2.f_rake_91, 0) <> 0) OR
                (gt.game_type = 92 AND IFNULL(apmm2.f_rake_92, 0) <> 0) OR
                (gt.game_type = 93 AND IFNULL(apmm2.f_rake_93, 0) <> 0) OR
                (gt.game_type = 94 AND IFNULL(apmm2.f_rake_94, 0) <> 0) OR
                (gt.game_type = 95 AND IFNULL(apmm2.f_rake_95, 0) <> 0) OR
                (gt.game_type = 96 AND IFNULL(apmm2.f_rake_96, 0) <> 0) OR
                (gt.game_type = 97 AND IFNULL(apmm2.f_rake_97, 0) <> 0) OR
                (gt.game_type = 98 AND IFNULL(apmm2.f_rake_98, 0) <> 0) OR
                (gt.game_type = 99 AND IFNULL(apmm2.f_rake_99, 0) <> 0) OR
                (gt.game_type = 100 AND IFNULL(apmm2.f_rake_100, 0) <> 0) OR
                (gt.game_type = 101 AND IFNULL(apmm2.f_rake_101, 0) <> 0) OR
                (gt.game_type = 102 AND IFNULL(apmm2.f_rake_102, 0) <> 0) OR
                (gt.game_type = 103 AND IFNULL(apmm2.f_rake_103, 0) <> 0) OR
                (gt.game_type = 104 AND IFNULL(apmm2.f_rake_104, 0) <> 0)
            )
        )
        AND apmm.f_player_id IN (
            SELECT f_player_id
            FROM t_analytics_players_money_monthly apmm3
            WHERE apmm3.f_timestamp = 'LAST_MONTH_END'
            AND apmm3.f_money_type = apmm.f_money_type
            AND (
                (gt.game_type = 34 AND IFNULL(apmm3.f_rake_34, 0) <> 0) OR
                (gt.game_type = 35 AND IFNULL(apmm3.f_rake_35, 0) <> 0) OR
                (gt.game_type = 54 AND IFNULL(apmm3.f_rake_54, 0) <> 0) OR
                (gt.game_type = 55 AND IFNULL(apmm3.f_rake_55, 0) <> 0) OR
                (gt.game_type = 63 AND IFNULL(apmm3.f_rake_63, 0) <> 0) OR
                (gt.game_type = 64 AND IFNULL(apmm3.f_rake_64, 0) <> 0) OR
                (gt.game_type = 65 AND IFNULL(apmm3.f_rake_65, 0) <> 0) OR
                (gt.game_type = 66 AND IFNULL(apmm3.f_rake_66, 0) <> 0) OR
                (gt.game_type = 67 AND IFNULL(apmm3.f_rake_67, 0) <> 0) OR
                (gt.game_type = 68 AND IFNULL(apmm3.f_rake_68, 0) <> 0) OR
                (gt.game_type = 69 AND IFNULL(apmm3.f_rake_69, 0) <> 0) OR
                (gt.game_type = 70 AND IFNULL(apmm3.f_rake_70, 0) <> 0) OR
                (gt.game_type = 71 AND IFNULL(apmm3.f_rake_71, 0) <> 0) OR
                (gt.game_type = 72 AND IFNULL(apmm3.f_rake_72, 0) <> 0) OR
                (gt.game_type = 73 AND IFNULL(apmm3.f_rake_73, 0) <> 0) OR
                (gt.game_type = 74 AND IFNULL(apmm3.f_rake_74, 0) <> 0) OR
                (gt.game_type = 75 AND IFNULL(apmm3.f_rake_75, 0) <> 0) OR
                (gt.game_type = 76 AND IFNULL(apmm3.f_rake_76, 0) <> 0) OR
                (gt.game_type = 77 AND IFNULL(apmm3.f_rake_77, 0) <> 0) OR
                (gt.game_type = 78 AND IFNULL(apmm3.f_rake_78, 0) <> 0) OR
                (gt.game_type = 79 AND IFNULL(apmm3.f_rake_79, 0) <> 0) OR
                (gt.game_type = 80 AND IFNULL(apmm3.f_rake_80, 0) <> 0) OR
                (gt.game_type = 81 AND IFNULL(apmm3.f_rake_81, 0) <> 0) OR
                (gt.game_type = 82 AND IFNULL(apmm3.f_rake_82, 0) <> 0) OR
                (gt.game_type = 83 AND IFNULL(apmm3.f_rake_83, 0) <> 0) OR
                (gt.game_type = 84 AND IFNULL(apmm3.f_rake_84, 0) <> 0) OR
                (gt.game_type = 85 AND IFNULL(apmm3.f_rake_85, 0) <> 0) OR
                (gt.game_type = 86 AND IFNULL(apmm3.f_rake_86, 0) <> 0) OR
                (gt.game_type = 87 AND IFNULL(apmm3.f_rake_87, 0) <> 0) OR
                (gt.game_type = 88 AND IFNULL(apmm3.f_rake_88, 0) <> 0) OR
                (gt.game_type = 89 AND IFNULL(apmm3.f_rake_89, 0) <> 0) OR
                (gt.game_type = 90 AND IFNULL(apmm3.f_rake_90, 0) <> 0) OR
                (gt.game_type = 91 AND IFNULL(apmm3.f_rake_91, 0) <> 0) OR
                (gt.game_type = 92 AND IFNULL(apmm3.f_rake_92, 0) <> 0) OR
                (gt.game_type = 93 AND IFNULL(apmm3.f_rake_93, 0) <> 0) OR
                (gt.game_type = 94 AND IFNULL(apmm3.f_rake_94, 0) <> 0) OR
                (gt.game_type = 95 AND IFNULL(apmm3.f_rake_95, 0) <> 0) OR
                (gt.game_type = 96 AND IFNULL(apmm3.f_rake_96, 0) <> 0) OR
                (gt.game_type = 97 AND IFNULL(apmm3.f_rake_97, 0) <> 0) OR
                (gt.game_type = 98 AND IFNULL(apmm3.f_rake_98, 0) <> 0) OR
                (gt.game_type = 99 AND IFNULL(apmm3.f_rake_99, 0) <> 0) OR
                (gt.game_type = 100 AND IFNULL(apmm3.f_rake_100, 0) <> 0) OR
                (gt.game_type = 101 AND IFNULL(apmm3.f_rake_101, 0) <> 0) OR
                (gt.game_type = 102 AND IFNULL(apmm3.f_rake_102, 0) <> 0) OR
                (gt.game_type = 103 AND IFNULL(apmm3.f_rake_103, 0) <> 0) OR
                (gt.game_type = 104 AND IFNULL(apmm3.f_rake_104, 0) <> 0)
            )
        )
    GROUP BY gt.GameType, apmm.f_money_type
) lc ON r.GameType = lc.GameType AND r.Currency = lc.Currency
ORDER BY r.GameType, r.Currency
```

> **4) Отчет по кэш играм с разбивкой по типам игр и лимитам**

```sql
SELECT 
    CASE atgm.f_game_type
        WHEN 0 THEN 'Unknown'
        WHEN 34 THEN 'CUSTOM'
        WHEN 35 THEN 'MIXED'
        WHEN 54 THEN 'SIXPLUSHOLDEM'
        WHEN 55 THEN 'TEENPATTI'
        WHEN 63 THEN 'RUMMYOKEY'
        WHEN 64 THEN 'RUMMYOKEYPOOL'
        WHEN 65 THEN 'RUMMYPOINTS'
        WHEN 66 THEN 'BADUGI'
        WHEN 67 THEN 'BADACEY'
        WHEN 68 THEN '27TRIPLEDRAW'
        WHEN 69 THEN 'BADEUCY'
        WHEN 70 THEN 'CHINESEOF'
        WHEN 71 THEN 'OMAHA5HL'
        WHEN 72 THEN 'HOLDEM'
        WHEN 73 THEN 'CHINESEOFPINEAPPLE'
        WHEN 74 THEN 'PINEAPPLEHOLDEM'
        WHEN 75 THEN 'TURKISH'
        WHEN 76 THEN 'CHINESEOF27PINEAPPLE'
        WHEN 77 THEN 'CHINESEOFPROGRPINEAPPLE'
        WHEN 78 THEN 'CHINESE'
        WHEN 79 THEN 'OMAHA'
        WHEN 80 THEN 'OMAHAHL'
        WHEN 81 THEN '7ADRAWHOLDEM'
        WHEN 82 THEN 'RAZZ'
        WHEN 83 THEN 'STUD'
        WHEN 84 THEN 'STUDHL'
        WHEN 85 THEN 'CHINESEOFTURBO'
        WHEN 86 THEN 'RUMMYDEALS'
        WHEN 87 THEN 'RUMMYPOOL'
        WHEN 88 THEN 'OMAHA5'
        WHEN 89 THEN 'COURCHEVEL'
        WHEN 90 THEN 'TRITONHOLDEM'
        WHEN 91 THEN 'OMAHA6'
        WHEN 92 THEN 'TELESINA'
        WHEN 93 THEN 'OMAHA6HL'
        WHEN 94 THEN '27SINGLEDRAW'
        WHEN 95 THEN 'TELESINAWITHVELA'
        WHEN 96 THEN '7ATELESINA'
        WHEN 97 THEN '7ATELESINAWITHVELA'
        WHEN 98 THEN 'CALLBREAK'
        WHEN 99 THEN 'BIG2'
        WHEN 100 THEN 'BIG2POOL'
        WHEN 101 THEN 'COWBOY'
        WHEN 102 THEN 'CHINESEOFULTIMATE'
        WHEN 103 THEN 'CHINESEOFJOKERS'
        WHEN 104 THEN 'CHINESEOFJOKERSULTIMATE'
        ELSE CAST(atgm.f_game_type AS CHAR)
    END AS GameType,
    c.f_iso_code AS Currency,
    ROUND(f_small_blind / POW(10, c.f_precision), c.f_precision) AS SmallBlind,
    ROUND(f_big_blind / POW(10, c.f_precision), c.f_precision) AS BigBlind,
    ROUND(SUM(IFNULL(atgm.f_rake, 0)) / POW(10, c.f_precision), c.f_precision) AS TotalRake,
    SUM(atgm.f_count_games) AS TotalGameCount
FROM t_analytics_tables_games_monthly atgm
LEFT JOIN t_table t ON t.f_id = atgm.f_table_id
INNER JOIN t_currency c ON c.f_money_type = atgm.f_money_type
WHERE atgm.f_timestamp = 'CURRENT_MONTH_END'
GROUP BY atgm.f_game_type, f_small_blind, f_big_blind, atgm.f_money_type
ORDER BY GameType, SmallBlind
```

>**5) Отчет по турнирам (без сателлитов, фрироллов)**

```sql
SELECT 
    tf.f_iso_code AS Currency,
    tf.TotalEntryFees,
    traf.TournamentRebuyAddonFees,
    tf.TournamentsCount,
    ta.AU AS TournamentAU,
    talm.AULastMonth AS TournamentAULastMonth,
    talc.AULastCurrent AS TournamentAULastCurrent
FROM 
    (
        SELECT
            atmm.f_money_type,
            c.f_iso_code,
            ROUND(SUM(IFNULL(atmm.f_entry_fee, 0))/POW(10, c.f_precision), c.f_precision) AS TotalEntryFees,
            COUNT(DISTINCT atmm.f_tournament_id) AS TournamentsCount
        FROM t_analytics_tournaments_money_monthly atmm
            LEFT JOIN t_tournament t ON t.f_id = atmm.f_tournament_id
            INNER JOIN t_currency c ON binary c.f_money_type = binary atmm.f_money_type
        WHERE atmm.f_timestamp = 'CURRENT_MONTH_END'
            AND (t.f_buy_in <> 0 OR t.f_entry_fee <> 0)
            AND t.f_parent_tournament_id = 0
        GROUP BY atmm.f_money_type
    ) tf
LEFT JOIN
    (
        SELECT 
            f_money_type,
            COUNT(DISTINCT f_player_id) AS AU
        FROM 
            t_analytics_players_money_monthly
        WHERE f_timestamp = 'CURRENT_MONTH_END'
            AND f_to_tournaments > 0
        GROUP BY f_money_type
    ) ta ON binary ta.f_money_type = binary tf.f_money_type
LEFT JOIN
    (
        SELECT 
            f_money_type,
            COUNT(DISTINCT f_player_id) AS AULastMonth
        FROM 
            t_analytics_players_money_monthly
        WHERE f_timestamp = 'LAST_MONTH_END'
            AND f_to_tournaments > 0
        GROUP BY f_money_type
    ) talm ON binary talm.f_money_type = binary tf.f_money_type
LEFT JOIN
    (
        SELECT 
            apmm.f_money_type,
            COUNT(DISTINCT apmm.f_player_id) AS AULastCurrent
        FROM 
            t_analytics_players_money_monthly apmm
        WHERE
            apmm.f_player_id IN (
                    SELECT f_player_id
                    FROM t_analytics_players_money_monthly
                    WHERE f_timestamp = 'LAST_MONTH_END'
                    AND f_to_tournaments > 0
                    AND f_money_type = apmm.f_money_type
                )
            AND apmm.f_player_id IN (
                    SELECT f_player_id
                    FROM t_analytics_players_money_monthly
                    WHERE f_timestamp = 'CURRENT_MONTH_END'
                    AND f_to_tournaments > 0
                    AND f_money_type = apmm.f_money_type
                )
        GROUP BY apmm.f_money_type
    ) talc ON binary talc.f_money_type = binary tf.f_money_type
LEFT JOIN
    (
        SELECT 
            apmm.f_money_type,
            ROUND(SUM(IFNULL(apmm.f_rebuy_addon_fee, 0))/POW(10, c.f_precision), c.f_precision) AS TournamentRebuyAddonFees
        FROM t_analytics_players_money_monthly apmm
            LEFT JOIN t_currency c ON binary c.f_money_type = binary apmm.f_money_type
        WHERE apmm.f_timestamp = 'CURRENT_MONTH_END'
        GROUP BY apmm.f_money_type
    ) traf ON binary traf.f_money_type = binary tf.f_money_type
```

>**6) Отчет по Sit&Go**

```sql
SELECT
    c.f_iso_code AS Currency,
    ROUND(SUM(IFNULL(atmm.f_entry_fee, 0))/POW(10, c.f_precision), c.f_precision) AS 'Total Entry Fees',
    COUNT(DISTINCT atmm.f_tournament_id) AS 'Tournaments Count'
FROM t_analytics_tournaments_money_monthly atmm
    LEFT JOIN t_tournament t ON t.f_id = atmm.f_tournament_id AND binary t.f_money_type = binary atmm.f_money_type
    INNER JOIN t_currency c ON binary c.f_money_type = binary atmm.f_money_type
WHERE t.f_prize_distribution = 'T' 
    AND t.f_tournament_type = 'G'
    AND atmm.f_timestamp = 'CURRENT_MONTH_END'
    AND t.f_parent_tournament_id = 0
    AND (t.f_buy_in <> 0 OR t.f_entry_fee <> 0)
GROUP BY atmm.f_money_type
```

>**7) Отчет по Spin&Go**

```sql
SELECT
    c.f_iso_code AS Currency,
    ROUND(SUM(IFNULL(atmm.f_entry_fee, 0))/POW(10, c.f_precision), c.f_precision) AS 'Total Entry Fees',
    COUNT(DISTINCT atmm.f_tournament_id) AS 'Tournaments Count'
FROM t_analytics_tournaments_money_monthly atmm
    LEFT JOIN t_tournament t ON t.f_id = atmm.f_tournament_id 
        AND binary t.f_money_type = binary atmm.f_money_type
    INNER JOIN t_currency c ON binary c.f_money_type = binary atmm.f_money_type
WHERE t.f_prize_distribution = 'P'
    AND atmm.f_timestamp = 'CURRENT_MONTH_END'
    AND t.f_parent_tournament_id = 0
    AND (t.f_buy_in <> 0 OR t.f_entry_fee <> 0)
GROUP BY atmm.f_money_type
```

>**8) Отчет по турнирам (без Sit&Go, Spin&Go, фрироллов и сателлитов)**

```sql
SELECT
    c.f_iso_code AS Currency,
    ROUND(SUM(IFNULL(atmm.f_entry_fee, 0))/POW(10, c.f_precision), c.f_precision) AS 'Total Entry Fees',
    COUNT(DISTINCT atmm.f_tournament_id) AS 'Tournaments Count'
FROM t_analytics_tournaments_money_monthly atmm
    LEFT JOIN t_tournament t ON t.f_id = atmm.f_tournament_id 
        AND binary t.f_money_type = binary atmm.f_money_type
    INNER JOIN t_currency c ON binary c.f_money_type = binary atmm.f_money_type
WHERE atmm.f_timestamp = 'CURRENT_MONTH_END'
    AND (t.f_buy_in <> 0 OR t.f_entry_fee <> 0)
    AND t.f_parent_tournament_id = 0
    AND t.f_tournament_type != 'G'
    AND t.f_prize_distribution != 'P'
GROUP BY atmm.f_money_type
```
"""
# Заменяем плейсхолдеры на актуальные даты
    sql_query = sql_template.replace("CURRENT_MONTH_END", current_month_end_str)
    sql_query = sql_query.replace("LAST_MONTH_END", last_month_end_str)
    sql_query = sql_query.replace("FIRST_DAY_CURRENT", first_day_current_str)

    return sql_query

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Выгрузка данных")
            # Словарь проектов и их UTC offset
        
        self.projects = {
            'WinZO': 0,
            '1Win': 0,
            'MPL Poker': 5.5,
            'Moonwalk': 5.5,
            'WePlay': 2,
            'Clubs Poker': -4,
            'Stake Poker Com': 0
        }
        
        # Переменные для хранения выбора
        self.project_var = tk.StringVar()
        self.date_var = tk.StringVar()
        
        # Флаг для отслеживания открытости второго окна
        self.second_window_open = False
        
        # Создаем основной интерфейс
        self.create_widgets()
        
        # Начальное состояние кнопки "Выгрузить"
        self.update_export_button_state()
        
        # Отслеживаем изменения в полях
        self.project_var.trace_add("write", self.on_field_change)
        self.date_var.trace_add("write", self.on_field_change)
    
    def create_widgets(self):
        # Фрейм для основного содержимого
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Проект (выпадающий список только для выбора)
        ttk.Label(main_frame, text="Проект:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.project_combobox = ttk.Combobox(main_frame, textvariable=self.project_var, state='readonly')
        self.project_combobox.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.project_combobox['values'] = tuple(self.projects.keys())
        
        # Дата (месяц/год)
        ttk.Label(main_frame, text="Дата (MM-YYYY):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(main_frame, textvariable=self.date_var)
        self.date_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Кнопка "Выгрузить"
        self.export_button = ttk.Button(main_frame, text="Выгрузить", command=self.open_second_window)
        self.export_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Настройка расширения колонок
        main_frame.columnconfigure(1, weight=1)
    
    def on_field_change(self, *args):
        self.update_export_button_state()
    
    def update_export_button_state(self):
        # Проверяем, заполнены ли поля и правильно ли введена дата
        project_selected = bool(self.project_var.get())
        date_valid = self.validate_date_format()
        
        # Устанавливаем состояние кнопки
        self.export_button['state'] = tk.NORMAL if (project_selected and date_valid and not self.second_window_open) else tk.DISABLED
    
    def validate_date_format(self):
        date_str = self.date_var.get()
        try:
            # Пытаемся разобрать дату в указанном формате
            datetime.strptime(date_str, "%m-%Y")
            return True
        except ValueError:
            return False
    
    def open_second_window(self):
    # Создаем второе окно
        self.second_window_open = True
        self.update_export_button_state()
        
        second_window = tk.Toplevel(self.root)
        second_window.title("Результат выгрузки")
        
        # Устанавливаем обработчик закрытия окна
        second_window.protocol("WM_DELETE_WINDOW", lambda: self.on_second_window_close(second_window))
        
        # Текстовое поле с результатом (только для чтения)
        result_text = tk.Text(second_window, wrap=tk.WORD, width=80, height=20, state='disabled')
        result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Генерируем текст для отображения
        project = self.project_var.get()
        date = self.date_var.get()
        utc_offset = self.projects[project]
    
        markdown_comment = generate_markdown_comment(date, utc_offset)
        
        display_text = f"Данные для проекта: {project} (UTC offset: {utc_offset})\nДата: {date}\n\n{markdown_comment}"
        
        # Вставляем текст с временным включением редактирования
        result_text.config(state='normal')
        result_text.insert(tk.END, display_text)
        result_text.config(state='disabled')
        
        # Кнопка "Копировать"
        copy_button = ttk.Button(second_window, text="Копировать", 
                               command=lambda: self.copy_to_clipboard(result_text.get("1.0", tk.END)))
        copy_button.pack(pady=5)
    
    def copy_to_clipboard(self, text):
        try:
            pyperclip.copy(text)
            messagebox.showinfo("Успех", "Текст скопирован в буфер обмена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скопировать текст: {e}")
    
    def on_second_window_close(self, window):
        self.second_window_open = False
        window.destroy()
        self.update_export_button_state()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    
    # Установка минимального размера окна
    root.minsize(400, 200)
    
    # Центрирование окна
    window_width = 500
    window_height = 250
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    root.mainloop()