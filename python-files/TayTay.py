import pandas as pd

# Creating the master list data
data = {
    "Jack Hughes": [
        # Lover
        "I Forgot That You Existed", "Paper Rings", "London Boy", "You Need to Calm Down", "It’s Nice to Have a Friend",
        # 1989
        "Shake It Off", "Style", "Blank Space", "How You Get the Girl", "Welcome to New York", "Suburban Legends*", "Is It Over Now?*",
        # Midnights
        "Bejeweled", "Karma", "Lavender Haze", "Paris", "Hits Different", "Glitch",
        # Fearless
        "You Belong With Me", "Hey Stephen", "Jump Then Fall", "Fearless", "Today Was a Fairytale", "That’s When*",
        # Red
        "22", "Stay Stay Stay", "We Are Never Ever Getting Back Together", "Holy Ground", "Message in a Bottle*", "The Very First Night*", "Come Back… Be Here",
        # Speak Now
        "Sparks Fly", "Mine", "Ours", "Superman", "Electric Touch*", "I Can See You*",
        # Reputation
        "...Ready For It?", "Gorgeous", "King of My Heart", "Don’t Blame Me", "Getaway Car",
        # Folklore
        "Betty", "August", "The 1", "Mirrorball", "Seven",
        # Evermore
        "Long Story Short", "Gold Rush", "Cowboy Like Me", "Ivy", "Right Where You Left Me*",
        # TTPD Anthology
        "Fortnight", "Down Bad", "Florida!!!", "But Daddy I Love Him", "My Boy Only Breaks His Favorite Toys", "So High School"
    ],
    "Quinn Hughes": [
        # Lover
        "The Archer", "Cornelia Street", "Afterglow", "Daylight", "Soon You’ll Get Better", "Miss Americana & The Heartbreak Prince",
        # 1989
        "This Love", "Clean", "You Are in Love", "Wildest Dreams", "I Wish You Would", "Say Don’t Go*", "Now That We Don’t Talk*",
        # Midnights
        "Maroon", "You’re On Your Own, Kid", "Sweet Nothing", "Dear Reader", "Bigger Than The Whole Sky", "Would’ve, Could’ve, Should’ve", "Question…?",
        # Fearless
        "White Horse", "The Way I Loved You", "Breathe", "Come In With the Rain", "Forever & Always (Piano Version)", "Don’t You*",
        # Red
        "All Too Well (10 Minute Version)", "Sad Beautiful Tragic", "The Last Time", "Begin Again", "Nothing New*", "Forever Winter*",
        # 1989
        "This Love", "Clean", "You Are in Love", "Wildest Dreams", "I Wish You Would", "Say Don’t Go*", "Now That We Don’t Talk*",
        # Speak Now
        "Back to December", "Enchanted", "Last Kiss", "Never Grow Up", "When Emma Falls in Love*", "Castles Crumbling*",
        # Reputation
        "Delicate", "Call It What You Want", "New Year’s Day", "Dancing With Our Hands Tied",
        # Folklore
        "Cardigan", "Peace", "Hoax", "Invisible String", "This Is Me Trying",
        # Evermore
        "Willow", "Champagne Problems", "Coney Island", "Evermore", "Marjorie",
        # TTPD Anthology
        "The Tortured Poets Department", "Clara Bow", "Cassandra", "The Black Dog", "The Manuscript", "The Prophecy"
    ],
    "Connor Bedard": [
        # Lover
        "The Man", "Cruel Summer", "Me!", "I Think He Knows",
        # 1989
        "Out of the Woods", "Wonderland", "New Romantics", "All You Had to Do Was Stay", "I Know Places", "Slut!*", "Say Don’t Go*",
        # Midnights
        "Anti-Hero", "Mastermind", "Midnight Rain", "The Great War", "High Infidelity",
        # Fearless
        "Fifteen", "You’re Not Sorry", "Untouchable", "If This Was a Movie", "Bye Bye Baby*", "We Were Happy*",
        # Red
        "Everything Has Changed", "Treacherous", "I Almost Do", "Run*", "Forever Winter (optional removed)", 
        # Speak Now
        "Dear John", "Innocent", "Haunted", "Long Live", "Foolish One*", "Timeless*",
        # Reputation
        "End Game", "I Did Something Bad", "So It Goes…", "Look What You Made Me Do", "Dress",
        # Folklore
        "Exile", "Illicit Affairs", "Epiphany", "My Tears Ricochet", "The Lakes",
        # Evermore
        "Tis the Damn Season", "Dorothea", "Happiness", "It’s Time to Go", "Evermore*",
        # TTPD Anthology
        "I Can Do It with a Broken Heart", "Who’s Afraid of Little Old Me?", "I Can Fix Him (No Really I Can)", "Fresh Out The Slammer", "Guilty as Sin?", "How Did It End?"
    ]
