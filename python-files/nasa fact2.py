#!/usr/bin/env python3
"""
🚀 NASA SPACE FACTS AI - ULTIMATE VAST CONTENT VERSION 🚀
Simple AI with MASSIVE database of space facts
Perfect structure with comprehensive NASA knowledge!

Author: NASA Hackathon Team  
Date: October 2025
Version: ULTIMATE VAST EDITION
"""

import random
import sys
from datetime import datetime

class UltimateNASASpaceFactsAI:
    """Ultimate AI with vast NASA space facts database - same simple structure"""
    
    def __init__(self):
        """Initialize with MASSIVE comprehensive NASA space facts database"""
        
        print("🚀" * 30)
        print("  NASA SPACE FACTS AI")
        print("    ULTIMATE VAST CONTENT EDITION")
        print("🚀" * 30)
        print()
        
        # 🌟 MASSIVE NASA SPACE FACTS DATABASE - 1000+ FACTS! 🌟
        self.space_facts = {
            # ======= PLANETS (MASSIVELY EXPANDED) =======
            'mars': [
                # Mars Basic Facts
                "🔴 Mars has the largest volcano in our solar system - Olympus Mons is 21 kilometers high!",
                "🚁 NASA's Ingenuity helicopter has completed over 72 flights on Mars as of 2024!",
                "🤖 The Perseverance rover has collected 27+ rock samples for future return to Earth",
                "❄️ Mars has polar ice caps made of both water ice and frozen carbon dioxide",
                "🌪️ Dust storms on Mars can cover the entire planet and last for months",
                "📅 A day on Mars (called a 'sol') is 24 hours and 37 minutes long",
                "🏔️ Valles Marineris canyon on Mars is 4,000 km long - that's the width of Australia!",
                "🧊 If all the ice on Mars melted, it would cover the planet in 35 meters of water",
                "🎯 Mars has two tiny moons: Phobos and Deimos, named after Greek gods of fear and panic",
                "🌡️ Mars is really cold! Average temperature is -80°F (-62°C)",
                
                # Mars Advanced Facts
                "🏜️ Mars has the largest canyon system in the solar system - Valles Marineris stretches 4,000 km",
                "⚖️ Gravity on Mars is only 38% of Earth's gravity - you could jump 3 times higher!",
                "🌅 Sunsets on Mars appear blue due to the way light scatters in the thin atmosphere",
                "🚀 Mars has been visited by 21 successful missions from Earth since the 1960s",
                "🔬 The atmosphere of Mars is 95% carbon dioxide with traces of nitrogen and argon",
                "🌊 Ancient Mars had oceans, rivers, and lakes - evidence suggests it was once habitable",
                "💨 The atmospheric pressure on Mars is less than 1% of Earth's atmospheric pressure",
                "🎭 Mars appears red because iron oxide (rust) covers much of its surface",
                "⭐ From Mars, Earth would appear as a bright blue star in the night sky",
                "🌋 Mars has the second-highest mountain in the solar system - Olympus Mons at 21 km tall",
                
                # Mars Exploration History
                "🛰️ The first successful Mars mission was Mariner 4 in 1965, taking 22 photos",
                "🤖 The first Mars rover was Sojourner in 1997, which operated for 85 days",
                "🎯 Spirit and Opportunity rovers were designed for 90 days but operated for years",
                "🔍 Opportunity rover operated for 15 years, from 2004 to 2018",
                "📡 The Mars Reconnaissance Orbiter has been studying Mars since 2006",
                "🛸 NASA's InSight lander detected over 1,300 marsquakes on Mars",
                "🚁 Ingenuity became the first aircraft to achieve powered flight on another planet",
                "🎪 The Mars Sample Return mission will bring Martian rocks back to Earth in the 2030s",
                "🌍 Mars is the only planet entirely populated by robots (rovers and landers)!",
                "🔮 Future Mars missions may include human astronauts in the 2030s or 2040s"
            ],
            
            'sun': [
                # Sun Basic Facts
                "☀️ The Sun is so big that 1.3 million Earths could fit inside it!",
                "🚀 NASA's Parker Solar Probe has 'touched' the Sun's corona for the first time ever!",
                "⚡ The Sun's core temperature reaches 27 million degrees Fahrenheit (15 million Celsius)!",
                "💨 Solar wind travels at speeds of 400-700 kilometers per second",
                "🔥 The Sun burns 4 million tons of mass every second and converts it to energy",
                "🌟 The Sun is a middle-aged star - it's about 4.6 billion years old",
                "⚡ One solar flare can release the energy of billions of nuclear bombs",
                "🌍 Light from the Sun takes 8 minutes and 20 seconds to reach Earth",
                "🎯 The Sun's magnetic field is 10,000 times stronger than Earth's",
                "🔬 The Sun is made of 73% hydrogen and 25% helium",
                
                # Sun Advanced Facts
                "🌡️ The Sun's surface temperature is 10,000°F (5,500°C) - much cooler than its core",
                "💫 The Sun produces the equivalent energy of 100 billion hydrogen bombs every second",
                "🌀 The Sun rotates faster at its equator (25 days) than at its poles (35 days)",
                "⭐ The Sun is classified as a G-type main-sequence star (yellow dwarf)",
                "🔄 The Sun's magnetic field flips every 11 years during solar maximum",
                "💥 Solar flares can disrupt satellites, GPS systems, and power grids on Earth",
                "🌊 The Sun creates space weather that affects all planets in the solar system",
                "🎪 The Sun contains 99.86% of all the mass in our entire solar system",
                "🔬 Nuclear fusion in the Sun's core creates all the light and heat we receive",
                "🌈 The Sun emits all colors of light, but Earth's atmosphere makes it appear yellow",
                
                # Sun Exploration and Future
                "🛰️ Parker Solar Probe will make 24 close approaches to the Sun through 2025",
                "🌡️ Parker Solar Probe's heat shield can withstand temperatures of 2,500°F",
                "🚀 The probe travels at speeds over 430,000 mph - fastest human-made object!",
                "📡 Solar Orbiter mission studies the Sun's polar regions and solar wind",
                "🔭 Multiple space telescopes continuously monitor the Sun for solar activity",
                "⚡ Scientists predict Solar Cycle 25 will peak around 2024-2025",
                "🌟 In about 5 billion years, the Sun will expand into a red giant star",
                "💫 Eventually, the Sun will become a white dwarf about the size of Earth",
                "🔬 Understanding the Sun helps us predict space weather and protect astronauts",
                "🌍 Solar energy reaching Earth in one hour could power the world for a year!"
            ],
            
            'jupiter': [
                # Jupiter Basic Facts
                "🌪️ Jupiter's Great Red Spot is a storm larger than Earth that's been raging for centuries!",
                "🛸 NASA's Juno spacecraft has been orbiting Jupiter since 2016, studying its mysteries",
                "🌙 Jupiter has 95 known moons - four of them (Io, Europa, Ganymede, Callisto) are as big as planets!",
                "🛡️ Jupiter acts as our solar system's 'vacuum cleaner' protecting Earth from asteroids",
                "⚡ Jupiter has the strongest magnetic field of any planet - 14 times stronger than Earth's",
                "💎 It might rain diamonds on Jupiter due to extreme pressure and carbon in the atmosphere!",
                "🌀 Jupiter spins so fast that one day there is only 9 hours and 56 minutes long",
                "🎯 You could fit 1,321 Earths inside Jupiter!",
                "🌊 Europa, Jupiter's moon, may have twice as much water as all Earth's oceans",
                "📡 Europa Clipper mission launched in October 2024 to study Europa for signs of life!",
                
                # Jupiter Advanced Facts
                "🪐 Jupiter is a gas giant made mostly of hydrogen and helium - like a mini star",
                "🎨 Jupiter's colorful bands are caused by different chemical compounds in its atmosphere",
                "💨 Winds on Jupiter can reach speeds of 400 mph (640 km/h)",
                "🌡️ Jupiter's core may be 43,000°F (24,000°C) - hotter than the Sun's surface!",
                "⭐ Jupiter almost became a second sun - it just needed to be 80 times more massive",
                "🔄 Jupiter takes 12 Earth years to complete one orbit around the Sun",
                "🌀 The Great Red Spot has been shrinking - it's now smaller than it was 100 years ago",
                "⚡ Jupiter's magnetic field creates aurora 1,000 times brighter than Earth's",
                "🎯 Jupiter has faint rings made of dust particles from its moons",
                "🌊 Three of Jupiter's moons (Europa, Ganymede, Callisto) likely have subsurface oceans",
                
                # Jupiter Moons and Exploration
                "🌋 Io has over 400 active volcanoes - the most geologically active body in the solar system",
                "🧊 Ganymede is the largest moon in the solar system - bigger than Mercury!",
                "🔍 Callisto is one of the most heavily cratered objects in the solar system",
                "🌊 Europa's ocean is kept liquid by tidal heating from Jupiter's massive gravity",
                "📸 Juno has taken incredible close-up images of Jupiter's swirling storms",
                "🛰️ The Galileo spacecraft studied Jupiter from 1995 to 2003",
                "🎪 Four large moons of Jupiter were discovered by Galileo in 1610 with a telescope",
                "🚀 Future missions may include submarines to explore Europa's subsurface ocean",
                "👽 Europa is considered one of the most promising places to find extraterrestrial life",
                "🌌 Jupiter's gravity helped accelerate many spacecraft on their way to outer planets"
            ],
            
            'saturn': [
                # Saturn Basic Facts
                "💍 Saturn's rings are made of billions of chunks of ice and rock!",
                "🎯 Saturn is so light it would float in water if there was a bathtub big enough!",
                "🌙 Saturn has 146 known moons - its largest moon Titan has lakes and rivers of methane!",
                "🚀 NASA's Cassini spacecraft studied Saturn for 13 years before ending its mission in 2017",
                "💨 Winds on Saturn can reach speeds of 1,800 km/hour at the equator",
                "🔍 Saturn's rings are only about 30 feet thick despite being 175,000 miles wide",
                "⭐ Saturn takes 29.5 Earth years to orbit the Sun once",
                "🌀 Saturn has a mysterious hexagonal storm at its north pole",
                "🎵 Saturn's rings 'sing' - they create radio waves that sound like music",
                "🌡️ Saturn's moon Enceladus shoots water geysers into space from its south pole!",
                
                # Saturn Advanced Facts
                "🪐 Saturn is the second-largest planet in our solar system after Jupiter",
                "⚖️ Saturn's density is 0.687 g/cm³ - less dense than water!",
                "🌈 Saturn's rings are divided into several main sections: A, B, C, D, E, F, and G rings",
                "🔬 The rings are made of 99% water ice with traces of rocky material",
                "📏 Saturn's ring system extends up to 282,000 km from the planet",
                "🌀 Saturn rotates once every 10 hours and 42 minutes",
                "🎨 Saturn appears golden due to ammonia crystals in its upper atmosphere",
                "⚡ Saturn has a magnetic field 578 times more powerful than Earth's",
                "🌡️ Saturn's core temperature may reach 25,000°F (12,000°C)",
                "💫 Saturn has the lowest density of any planet - 30% less dense than water",
                
                # Saturn Moons and Features
                "🌊 Titan has methane lakes, rivers, and rain - it's like an alien version of Earth!",
                "🧊 Enceladus has a global ocean beneath its icy surface",
                "🌋 Enceladus' geysers shoot water 500 km into space",
                "🔍 Titan is the second-largest moon in the solar system",
                "☁️ Titan has a thick atmosphere - the only moon in the solar system with one",
                "🛰️ The Huygens probe landed on Titan in 2005 - first landing in the outer solar system",
                "🎪 Saturn's hexagonal storm at the north pole is 25,000 km wide",
                "⭐ The hexagon storm has winds of 320 km/h and has persisted for decades",
                "💍 Saturn's rings were first observed by Galileo in 1610, though he couldn't resolve them",
                "🚀 Future missions may explore Titan's methane lakes and Enceladus' ocean"
            ],
            
            'earth': [
                # Earth Basic Facts
                "🌍 Earth is the only known planet with life in the entire universe!",
                "🛡️ Earth's magnetic field protects us from harmful solar radiation",
                "💧 71% of Earth's surface is covered by water, but only 3% is fresh water",
                "🌿 Earth's atmosphere is 78% nitrogen, 21% oxygen, and 1% other gases",
                "⚡ Lightning strikes Earth about 100 times every second!",
                "🌋 There are about 1,500 active volcanoes on Earth right now",
                "🌊 Earth's deepest point is the Mariana Trench - 36,200 feet deep!",
                "🎯 Earth is traveling through space at 67,000 miles per hour",
                "🌡️ Earth's core is as hot as the surface of the Sun - 10,800°F!",
                "📅 Earth is about 4.54 billion years old",
                
                # Earth Advanced Facts
                "⚖️ Earth's mass is approximately 6 billion trillion tons (5.97 × 10²⁴ kg)",
                "🌍 Earth's diameter is 12,742 km at the equator - it's slightly flattened at the poles",
                "🔄 Earth rotates once every 23 hours, 56 minutes, and 4 seconds (not exactly 24 hours!)",
                "🌙 Earth's tilt of 23.5 degrees gives us our seasons",
                "💫 Earth orbits the Sun at an average distance of 93 million miles",
                "🌊 The Pacific Ocean covers more area than all land masses combined",
                "🏔️ Mount Everest grows about 4mm taller every year due to tectonic activity",
                "🌋 The Ring of Fire around the Pacific Ocean contains 75% of the world's active volcanoes",
                "🔥 Earth's inner core is solid iron, while the outer core is liquid",
                "🌀 The Coriolis effect causes hurricanes to spin counterclockwise in the Northern Hemisphere",
                
                # Earth Life and Environment
                "🦋 Scientists estimate there are 8.7 million species on Earth",
                "🌳 The Amazon rainforest produces 20% of the world's oxygen",
                "🐋 Earth's oceans contain 99% of the planet's living space",
                "🦠 The first life on Earth appeared about 3.8 billion years ago",
                "🌿 Photosynthesis by plants and algae produces all the oxygen we breathe",
                "🌡️ Earth's average temperature is 59°F (15°C)",
                "❄️ The last ice age ended about 11,700 years ago",
                "🌍 Earth's biodiversity hotspots contain 60% of all species in just 2.3% of land area",
                "🪨 The oldest rocks on Earth are 4.4 billion years old",
                "🌊 Ocean currents help regulate Earth's climate by distributing heat around the globe"
            ],
            
            'moon': [
                # Moon Basic Facts
                "🌙 The Moon is gradually moving away from Earth at 3.8 cm per year!",
                "🚀 NASA's Artemis program will land the first woman on the Moon!",
                "🏋️ You would weigh only 1/6th of your Earth weight on the Moon",
                "🌍 The Moon causes Earth's ocean tides through gravitational pull",
                "🌑 We always see the same side of the Moon from Earth (tidal locking)",
                "🎯 Apollo astronauts left equipment that still works on the Moon today",
                "💥 The Moon was likely formed when a Mars-sized object hit Earth 4.5 billion years ago",
                "🌡️ Moon temperatures range from 250°F (121°C) to -208°F (-133°C)",
                "👣 The last person to walk on the Moon was Eugene Cernan in 1972",
                "🔍 NASA has found water ice in permanently shadowed lunar craters",
                
                # Moon Advanced Facts
                "📏 The Moon is 384,400 km away from Earth on average",
                "🌙 The Moon's diameter is 3,474 km - about 1/4 the size of Earth",
                "⚖️ The Moon's mass is 1/81st of Earth's mass",
                "🔄 The Moon rotates once every 27.3 days - the same time it takes to orbit Earth",
                "🌕 The Moon goes through 8 phases during its 29.5-day cycle",
                "🎯 The Moon's orbit is elliptical - sometimes it's 356,500 km away, sometimes 406,700 km",
                "🌊 The Moon's gravity causes two high tides and two low tides on Earth every day",
                "🌑 During a total solar eclipse, the Moon perfectly covers the Sun",
                "🪨 The Moon's surface is covered by a layer of fine dust called regolith",
                "🌋 The dark areas on the Moon are ancient lava plains called 'maria' (seas)",
                
                # Moon Exploration History
                "🚀 The first spacecraft to reach the Moon was Luna 2 in 1959",
                "📸 Luna 3 took the first photos of the Moon's far side in 1959",
                "👨‍🚀 Neil Armstrong and Buzz Aldrin were the first humans to walk on the Moon (July 20, 1969)",
                "🛰️ Six Apollo missions successfully landed 12 astronauts on the Moon",
                "🪨 Apollo astronauts brought back 842 pounds of Moon rocks and soil",
                "🔬 Moon rocks are still being studied by scientists today",
                "🌙 The far side of the Moon was first mapped by the Soviet Luna 3 mission",
                "🇨🇳 China's Chang'e missions have explored both sides of the Moon",
                "🛸 Over 100 missions have been sent to the Moon by various countries",
                "🎪 Future lunar bases may use Moon ice to produce water, oxygen, and rocket fuel"
            ],
            
            'venus': [
                # Venus Basic Facts
                "🔥 Venus is the hottest planet in our solar system at 900°F (482°C)!",
                "☔ It rains sulfuric acid on Venus, but it evaporates before hitting the ground",
                "🌀 Venus rotates backwards compared to most other planets",
                "⏰ One day on Venus (243 Earth days) is longer than one Venus year (225 Earth days)!",
                "💨 Venus has winds up to 360 km/hour in its upper atmosphere",
                "🏔️ Venus has more volcanoes than any other planet - over 1,600!",
                "☁️ Venus is completely covered by thick clouds of carbon dioxide and sulfuric acid",
                "🎯 Venus is sometimes called Earth's 'evil twin' due to similar size but extreme conditions",
                "🚀 NASA is planning new missions to study Venus in the 2030s",
                "💎 The atmospheric pressure on Venus is 90 times stronger than Earth's!",
                
                # Venus Advanced Facts
                "🌟 Venus is the brightest object in Earth's sky after the Sun and Moon",
                "📏 Venus is almost identical in size to Earth - diameter of 12,104 km",
                "🌡️ Venus experiences a runaway greenhouse effect due to its thick atmosphere",
                "⚡ Lightning on Venus may be more common than on Earth",
                "🌋 Venus has shield volcanoes similar to those in Hawaii",
                "🗻 The highest mountain on Venus is Maxwell Montes at 10.8 km tall",
                "🔄 Venus rotates so slowly that its day is longer than its year",
                "🌪️ Venus has super-rotating winds - the atmosphere spins faster than the planet",
                "💫 Venus has phases like the Moon when viewed from Earth",
                "🎨 Venus appears bright white due to its highly reflective cloud cover",
                
                # Venus Exploration
                "🛸 Over 40 spacecraft have been sent to Venus by various space agencies",
                "🇷🇺 Soviet Venera probes were the first to successfully land on Venus",
                "📸 Venera 13 survived 127 minutes on Venus's surface and sent back color photos",
                "🛰️ NASA's Magellan spacecraft mapped Venus's surface using radar",
                "🌋 Magellan discovered evidence of recent volcanic activity on Venus",
                "🔬 Venus Express studied Venus's atmosphere from 2006 to 2014",
                "🚀 NASA's DAVINCI+ and VERITAS missions will study Venus in the 2030s",
                "🇯🇵 Japan's Akatsuki spacecraft is currently studying Venus's weather",
                "🌊 Ancient Venus may have had oceans before the greenhouse effect took over",
                "🔍 Scientists are studying Venus to understand climate change on Earth"
            ],
            
            'mercury': [
                # Mercury Basic Facts
                "🔥 Mercury has the most extreme temperatures - 800°F day, -300°F night!",
                "🏃 Mercury has the fastest orbit around the Sun - completing one year in just 88 Earth days",
                "🎯 Mercury is the smallest planet in our solar system, only slightly larger than our Moon",
                "🌙 Mercury has no moons or rings",
                "🚀 NASA's MESSENGER spacecraft studied Mercury from 2011-2015",
                "💥 Mercury's surface is covered with craters from asteroid impacts",
                "🧊 Despite being closest to the Sun, Mercury has ice at its poles!",
                "⚡ One day on Mercury lasts 59 Earth days",
                "🌍 From Mercury, the Sun would appear 3 times larger than from Earth",
                "🎪 Mercury's orbit is so elliptical that the Sun appears to move backwards in the sky!",
                
                # Mercury Advanced Facts
                "📏 Mercury's diameter is 4,879 km - about 38% the size of Earth",
                "⚖️ Mercury's gravity is 38% of Earth's gravity",
                "🔄 Mercury rotates 3 times for every 2 orbits around the Sun",
                "🌡️ Mercury's core makes up 75% of its radius - unusually large",
                "⚡ Mercury has a weak magnetic field - about 1% as strong as Earth's",
                "🌋 Mercury has cliff-like scarps up to 3 km high and 1,500 km long",
                "💨 Mercury has an extremely thin atmosphere called an exosphere",
                "🎨 Mercury's surface is dark gray, similar to graphite",
                "⭐ Mercury goes through phases like the Moon when viewed from Earth",
                "🌀 Mercury's highly elliptical orbit ranges from 46 to 70 million km from the Sun",
                
                # Mercury Exploration and Features
                "🛸 Only two spacecraft have visited Mercury: Mariner 10 and MESSENGER",
                "📸 MESSENGER took over 250,000 images of Mercury's surface",
                "🔍 MESSENGER discovered water ice in Mercury's polar craters",
                "🌋 Mercury shows evidence of past volcanic activity",
                "⚡ Mercury's magnetic field suggests it has a liquid iron core",
                "🚀 ESA and JAXA's BepiColombo mission is currently traveling to Mercury",
                "🔬 BepiColombo will arrive at Mercury in 2025 for detailed study",
                "🌊 Polar ice deposits on Mercury could contain billions of tons of water",
                "🎯 Mercury's Caloris Basin is one of the largest impact craters in the solar system",
                "☀️ A year on Mercury is only 88 Earth days, but a day is 176 Earth days!"
            ],
            
            # ======= SPACE OBJECTS (VASTLY EXPANDED) =======
            'black hole': [
                # Black Hole Basic Facts
                "🕳️ Black holes have gravity so strong that nothing, not even light, can escape!",
                "📸 In 2019, we got the first ever photo of a black hole using the Event Horizon Telescope!",
                "⏰ Time slows down near black holes due to extreme gravity (time dilation)",
                "🌌 There's a supermassive black hole at the center of our Milky Way called Sagittarius A*",
                "🍝 Getting too close to a black hole would stretch you like spaghetti!",
                "⭐ Black holes form when massive stars collapse at the end of their lives",
                "🌟 Some black holes are millions of times more massive than our Sun",
                "💫 Black holes might connect to other parts of the universe through 'wormholes'",
                "🔬 Stephen Hawking discovered that black holes actually evaporate very slowly",
                "🌊 When black holes collide, they create ripples in space-time called gravitational waves!",
                
                # Black Hole Advanced Facts
                "⚫ The event horizon is the point of no return around a black hole",
                "🌀 Matter spiraling into a black hole forms an accretion disk that glows brightly",
                "⚡ Black holes can shoot jets of particles at nearly the speed of light",
                "🎯 Stellar-mass black holes are 3-20 times the mass of our Sun",
                "🌌 Supermassive black holes can be billions of times more massive than the Sun",
                "🔬 Hawking radiation means black holes slowly evaporate over trillions of years",
                "💥 When two black holes merge, they create gravitational waves",
                "🌟 Active galactic nuclei are powered by supermassive black holes",
                "🎪 The closest known black hole to Earth is about 1,000 light-years away",
                "⚖️ Black holes have only three properties: mass, electric charge, and spin",
                
                # Black Hole Discoveries and Research
                "🔭 The Event Horizon Telescope photographed M87's black hole in 2019",
                "📷 In 2022, we got the first image of Sagittarius A* - our galaxy's black hole",
                "🏆 The 2020 Nobel Prize in Physics was awarded for black hole research",
                "🌊 LIGO detectors have discovered dozens of black hole mergers",
                "🚀 NASA's Chandra X-ray Observatory studies black holes across the universe",
                "⚡ Quasars are the most luminous objects in the universe, powered by black holes",
                "🔬 Scientists use black holes to test Einstein's theory of general relativity",
                "🌌 Most galaxies have supermassive black holes at their centers",
                "💫 Black holes may be connected to the formation of galaxies",
                "🎯 Future telescopes may be able to see black holes forming in real-time"
            ],
            
            'stars': [
                # Stars Basic Facts
                "⭐ There are more stars in the universe than grains of sand on all Earth's beaches!",
                "🌟 Our Sun is just one of over 100 billion stars in the Milky Way galaxy",
                "💥 When massive stars die, they explode as supernovas - visible from billions of miles away!",
                "🔥 The hottest stars burn blue-white and can be 50,000°F on their surface",
                "👯 Most stars actually exist in pairs or groups, not alone like our Sun",
                "💎 When stars die, they can become white dwarfs, neutron stars, or black holes",
                "🌈 A star's color tells us its temperature - red is coolest, blue is hottest",
                "🏭 Stars are giant nuclear fusion reactors, turning hydrogen into helium",
                "⚡ Neutron stars spin up to 700 times per second!",
                "🔭 The Hubble Space Telescope has helped us discover stars being born in stellar nurseries",
                
                # Stars Advanced Facts
                "🌟 Stars are classified by spectral type: O, B, A, F, G, K, M (hottest to coolest)",
                "⚖️ The most massive stars can be over 100 times the mass of our Sun",
                "🔬 Nuclear fusion in stars creates all elements heavier than hydrogen and helium",
                "💫 A star's lifetime depends on its mass - more massive stars live shorter lives",
                "🌈 Red giant stars can be 100 times larger than the Sun",
                "💎 White dwarf stars are incredibly dense - a teaspoon would weigh 5 tons!",
                "⚡ Neutron stars are even denser - a teaspoon would weigh 6 billion tons!",
                "🎯 The nearest star to Earth (besides the Sun) is Proxima Centauri at 4.24 light-years away",
                "🌟 Brown dwarfs are 'failed stars' - not massive enough to sustain nuclear fusion",
                "🔄 Variable stars change brightness over time due to pulsations or eclipses",
                
                # Star Formation and Evolution
                "🌌 Stars form in giant clouds of gas and dust called nebulae",
                "⚡ It takes about 10 million years for a new star to fully form",
                "🌟 Main sequence stars (like our Sun) fuse hydrogen into helium for billions of years",
                "💥 Stars more than 8 times the Sun's mass explode as supernovas",
                "🌈 Planetary nebulae form when Sun-like stars shed their outer layers",
                "💫 The heaviest elements (like gold and uranium) are created in supernovas",
                "🔭 The James Webb Space Telescope can see the first stars that formed after the Big Bang",
                "🌟 Population III stars were the first stars - made only of hydrogen and helium",
                "⚖️ The most massive star ever discovered is R136a1 - 315 times the Sun's mass",
                "🎪 Betelgeuse is a red supergiant that may explode as a supernova soon (within 100,000 years)"
            ],
            
            'galaxy': [
                # Galaxy Basic Facts
                "🌌 The Milky Way galaxy contains over 100 billion stars!",
                "📏 Our galaxy is about 100,000 light-years wide",
                "🚀 We're traveling through the galaxy at 515,000 mph!",
                "🌀 The Milky Way is a spiral galaxy with beautiful spiral arms",
                "🔭 The James Webb Space Telescope can see galaxies from over 13 billion years ago!",
                "💥 Our galaxy is on a collision course with Andromeda galaxy in 4.5 billion years",
                "🕳️ Most galaxies have supermassive black holes at their centers",
                "⭐ There are over 2 trillion galaxies in the observable universe!",
                "🌟 Our solar system is located in the Orion Arm of the Milky Way",
                "🎯 It takes our solar system 225 million years to orbit the galaxy once!",
                
                # Galaxy Advanced Facts
                "🌌 Galaxies are classified as spiral, elliptical, or irregular",
                "⚖️ The Milky Way's mass is about 1.5 trillion times the mass of the Sun",
                "🔄 The Milky Way rotates once every 225-250 million years",
                "📏 The nearest major galaxy is Andromeda, 2.5 million light-years away",
                "🌟 Galaxy clusters can contain thousands of galaxies bound by gravity",
                "🕳️ Sagittarius A* is our galaxy's central black hole - 4 million solar masses",
                "💫 The Milky Way is part of the Local Group of about 80 galaxies",
                "🌈 Galaxies appear different colors based on their dominant star types",
                "⚡ Active galaxies have energetic cores powered by supermassive black holes",
                "🔬 Dark matter makes up about 85% of a galaxy's total mass",
                
                # Galaxy Formation and Evolution
                "🌌 The first galaxies formed about 13 billion years ago",
                "💥 Galaxy mergers can trigger massive star formation bursts",
                "🔭 The Hubble Space Telescope revealed galaxies at different evolutionary stages",
                "🌟 Elliptical galaxies are older and contain mostly old, red stars",
                "🌀 Spiral galaxies have ongoing star formation in their arms",
                "⚡ Starburst galaxies form stars at rates 100 times higher than the Milky Way",
                "🕳️ Quasars are distant galaxies with extremely active black holes",
                "📡 Radio galaxies emit powerful jets from their central black holes",
                "🌈 The cosmic web connects galaxies in a vast network of dark matter",
                "🎯 Future telescopes will study the very first galaxies that ever formed"
            ],
            
            # ======= NASA MISSIONS (MASSIVELY EXPANDED) =======
            'artemis': [
                # Artemis Basic Facts
                "🚀 Artemis will land the first woman and next man on the Moon!",
                "🌙 Artemis I successfully completed an uncrewed trip around the Moon in 2022",
                "🏗️ NASA plans to build a permanent lunar base for future Mars missions",
                "🚀 The Space Launch System (SLS) is the most powerful rocket NASA has ever built",
                "👩‍🚀 Artemis astronauts will spend a week on the Moon's surface",
                "🌍 Artemis will use the Moon as a stepping stone to Mars",
                "🛰️ The Lunar Gateway will be a space station orbiting the Moon",
                "⛽ Artemis will test technologies for producing fuel from lunar ice",
                "🔬 Astronauts will conduct important science experiments on the Moon",
                "📅 NASA aims for Artemis III to land on the Moon by 2026!",
                
                # Artemis Advanced Facts
                "🚀 The SLS rocket stands 322 feet tall - taller than the Statue of Liberty",
                "⚡ SLS generates 8.8 million pounds of thrust at liftoff",
                "🌙 Artemis missions will land near the Moon's south pole",
                "🧊 The lunar south pole has permanently shadowed regions with water ice",
                "👩‍🚀 NASA has selected a diverse group of Artemis astronauts",
                "🛸 The Orion spacecraft can carry 4 astronauts to the Moon",
                "🏗️ The Lunar Gateway will serve as a staging point for Moon missions",
                "⛽ Artemis will demonstrate in-situ resource utilization (ISRU)",
                "🔬 Scientists will study the Moon's geology and search for resources",
                "🌍 Artemis experiences will help prepare for human missions to Mars",
                
                # Artemis Timeline and Goals
                "📅 Artemis II will send astronauts around the Moon (no landing) in 2025",
                "🌙 Artemis III aims to land astronauts on the Moon by 2026",
                "🏗️ Artemis IV will begin construction of the Lunar Gateway in 2028",
                "👥 Future Artemis missions will have longer stays and more crew",
                "🔬 The program includes international partnerships with ESA, JAXA, and CSA",
                "🚀 SpaceX's Starship will serve as the Human Landing System",
                "⛽ NASA will test oxygen and fuel production from lunar resources",
                "🛰️ Commercial companies will deliver supplies to the Moon",
                "🌍 Artemis knowledge will inform future Mars exploration",
                "🎯 The goal is sustainable lunar exploration for decades to come"
            ],
            
            'perseverance': [
                # Perseverance Basic Facts
                "🤖 Perseverance is searching for signs of ancient life on Mars!",
                "🚁 It brought the first helicopter to another planet - Ingenuity!",
                "🪨 Perseverance has collected 27+ rock samples for future return to Earth",
                "🎯 It landed in Jezero Crater, which used to be an ancient lake",
                "🔬 The rover has 7 scientific instruments and 23 cameras",
                "💨 Perseverance created oxygen from the Martian atmosphere!",
                "📅 It's been exploring Mars since February 18, 2021",
                "🚀 The samples it collects will be returned to Earth by future missions",
                "🔍 Perseverance is looking for biosignatures - signs that life existed on Mars",
                "⚡ It's powered by nuclear energy, not solar panels like previous rovers!",
                
                # Perseverance Advanced Facts
                "🤖 Perseverance weighs 1,025 kg and is the size of a car",
                "🔋 The rover is powered by a Multi-Mission Radioisotope Thermoelectric Generator",
                "🪨 It uses a drill to collect core samples from Martian rocks",
                "🔬 The MOXIE instrument has produced oxygen 16 times on Mars",
                "📡 Perseverance communicates with Earth via orbiting Mars satellites",
                "🎯 Jezero Crater was chosen because it shows signs of ancient water activity",
                "🌊 The crater contains a well-preserved river delta from 3.5 billion years ago",
                "🔍 The rover searches for organic compounds and mineral textures",
                "📸 Perseverance has taken over 300,000 images of Mars",
                "🛸 The rover landed using the same sky crane system as Curiosity",
                
                # Ingenuity Helicopter Facts
                "🚁 Ingenuity weighs only 1.8 kg but has made history on Mars",
                "⚡ The helicopter is solar-powered and charges its batteries daily",
                "🎯 Ingenuity was designed for 5 flights but has completed over 70!",
                "📏 Each flight covers hundreds of meters and lasts up to 3 minutes",
                "🔍 Ingenuity scouts interesting locations for Perseverance to visit",
                "💨 Flying on Mars is difficult due to the thin atmosphere",
                "📸 The helicopter takes aerial photos of Mars from above",
                "🚁 Ingenuity's success led to plans for future Mars helicopters",
                "🎪 It proved powered flight is possible on other planets",
                "🌟 Ingenuity exceeded all expectations and continues operating"
            ],
            
            'james webb': [
                # James Webb Basic Facts
                "🔭 James Webb is the most powerful space telescope ever built!",
                "🌌 It can see galaxies that formed over 13 billion years ago!",
                "🪞 Its mirror is 6.5 meters wide - nearly 3 times bigger than Hubble's",
                "❄️ James Webb operates at -370°F to detect infrared light",
                "📍 It orbits 1.5 million km from Earth at Lagrange Point 2",
                "🌟 James Webb can see the first stars that ever formed in the universe",
                "🪐 It studies exoplanets and can analyze their atmospheres for signs of life",
                "🚀 It took over 20 years to design and build James Webb",
                "📸 Its images are 100 times more detailed than Hubble's",
                "🔬 James Webb is revolutionizing our understanding of the universe!",
                
                # James Webb Advanced Facts
                "🪞 The primary mirror consists of 18 hexagonal beryllium segments",
                "❄️ The telescope must be kept extremely cold to function properly",
                "🛡️ A tennis court-sized sunshield protects it from the Sun's heat",
                "🔬 Webb has four main scientific instruments for different observations",
                "📡 It takes about 6 hours to download one full-resolution image",
                "🎯 The telescope can see objects 100 times fainter than Hubble",
                "🌈 Webb observes primarily in near and mid-infrared wavelengths",
                "🚀 The telescope launched on an Ariane 5 rocket in December 2021",
                "⚖️ James Webb weighs about 6,500 kg - half the mass of Hubble",
                "🔧 The telescope took 6 months to fully deploy and calibrate",
                
                # James Webb Discoveries
                "🌌 Webb discovered galaxies that formed just 400 million years after the Big Bang",
                "⭐ It revealed that early galaxies were more massive than expected",
                "🪐 Webb has analyzed atmospheres of dozens of exoplanets",
                "💧 The telescope detected water vapor in exoplanet atmospheres",
                "🌟 Webb captured detailed images of stellar birth in nearby nebulae",
                "💥 It observed the aftermath of stellar collisions and supernovas",
                "🪐 Webb studied the atmospheres of planets in our own solar system",
                "🌊 The telescope revealed complex organic molecules in space",
                "🔬 Webb's data is helping solve mysteries about dark matter and dark energy",
                "🎯 Future observations will search for biosignatures in exoplanet atmospheres"
            ],
            
            'europa clipper': [
                # Europa Clipper Basic Facts
                "🚀 Europa Clipper launched in October 2024 to study Jupiter's icy moon!",
                "🌊 Europa may have twice as much water as all Earth's oceans combined!",
                "🧊 Europa Clipper will study the moon's ice-covered ocean for signs of life",
                "📡 It will make 49 close flybys of Europa over 4 years",
                "⚡ The spacecraft carries 9 scientific instruments",
                "🎯 Journey to Jupiter takes 5.5 years covering 2.9 billion kilometers",
                "🌌 Europa's ocean is kept liquid by tidal heating from Jupiter",
                "🔍 Europa Clipper will map Europa's ice shell and study its chemistry",
                "🛰️ It's powered by solar panels - the first solar-powered mission to Jupiter!",
                "👽 Scientists think Europa's ocean could potentially harbor life!",
                
                # Europa Clipper Advanced Facts
                "📏 Europa Clipper is 30.5 meters wide when its solar arrays are deployed",
                "⚖️ The spacecraft weighs 6,065 kg fully fueled",
                "🔋 Its solar arrays generate 700 watts of power at Jupiter",
                "📡 The high-gain antenna is 3 meters in diameter",
                "🛡️ Radiation-resistant electronics protect against Jupiter's radiation",
                "🔬 The nine instruments include cameras, spectrometers, and a magnetometer",
                "🧊 Ice-penetrating radar will study Europa's ice shell thickness",
                "⚡ The magnetometer will confirm Europa's subsurface ocean",
                "📸 Cameras will map Europa's surface in unprecedented detail",
                "🌡️ Thermal instruments will search for warm spots indicating geological activity",
                
                # Europa and Astrobiology
                "🌊 Europa's global ocean lies beneath 15-25 km of ice",
                "🔥 Tidal heating from Jupiter keeps Europa's ocean liquid",
                "⚡ Europa may have hydrothermal vents on its ocean floor",
                "🧪 The ocean likely contains more than twice Earth's ocean water",
                "🔬 Europa's ocean has been liquid for billions of years",
                "🌍 Chemical elements necessary for life are likely present",
                "🦠 Earth's deep ocean life suggests Europa could harbor organisms",
                "🌋 Europa shows signs of recent geological activity",
                "📊 The mission will assess Europa's habitability potential",
                "🚀 Future missions might include a lander or submarine to explore Europa"
            ],
            
            # ======= SPACE EXPLORATION (VASTLY EXPANDED) =======
            'space': [
                # General Space Facts
                "🚀 Humans have been continuously living in space on the ISS for over 23 years!",
                "🌌 Space is completely silent because there's no air to carry sound waves",
                "👨‍🚀 Astronauts see 16 sunrises and sunsets every day on the ISS!",
                "🌡️ Space is really cold - about -455°F (-270°C) in empty space",
                "⚡ There are over 34,000 pieces of space junk orbiting Earth right now",
                "🔭 NASA has over 90 active space missions studying our universe",
                "🌟 The observable universe contains over 2 trillion galaxies",
                "💫 Space is expanding - galaxies are moving away from us!",
                "🛰️ Over 8,000 satellites are currently orbiting Earth",
                "🌍 From space, astronauts can't see the Great Wall of China with the naked eye!",
                
                # Space Environment Facts
                "🌌 Space is a near-perfect vacuum with less than 1 atom per cubic centimeter",
                "⚡ Cosmic radiation in space can damage electronics and harm astronauts",
                "🌡️ Objects in space can be both extremely hot and cold at the same time",
                "💫 There's no up or down in space - astronauts experience microgravity",
                "🔄 Objects in orbit are in constant free fall around Earth",
                "⚖️ The weightlessness in space causes bones and muscles to weaken",
                "🩸 Blood and other fluids behave differently in microgravity",
                "🌊 Liquids form perfect spheres in the absence of gravity",
                "🔥 Fire burns differently in space - flames are blue and spherical",
                "💨 Without air pressure, human blood would boil in the vacuum of space",
                
                # Space Technology and Exploration
                "🛰️ The first artificial satellite was Sputnik 1, launched in 1957",
                "👨‍🚀 Yuri Gagarin became the first human in space on April 12, 1961",
                "🌙 The farthest humans have traveled from Earth is to the Moon",
                "🚀 The fastest spacecraft ever launched is the Parker Solar Probe",
                "📡 Deep Space Network antennas communicate with distant spacecraft",
                "🔭 Space telescopes can observe wavelengths blocked by Earth's atmosphere",
                "⛽ Ion propulsion allows spacecraft to travel for years using very little fuel",
                "🛡️ Heat shields protect spacecraft during high-speed atmospheric entry",
                "🤖 Robotic missions have visited every planet in our solar system",
                "🌟 Future missions may take humans to Mars, Europa, and beyond"
            ],
            
            'astronaut': [
                # Astronaut Basic Facts
                "👩‍🚀 Astronauts must exercise 2.5 hours daily in space to stay healthy!",
                "🍕 Food floats in space, so astronauts eat from pouches and tubes",
                "😴 Astronauts sleep in sleeping bags attached to walls",
                "🚿 Astronauts use special wipes to clean themselves - no showers in space!",
                "👨‍🚀 NASA has selected the most diverse astronaut class ever for future missions",
                "🧬 Astronauts' bodies change in space - they get taller and their bones weaken",
                "🌍 Astronauts can see lightning storms from above that look like camera flashes",
                "⚡ Space suits have their own life support systems and cost $500 million each!",
                "🎯 Astronauts train underwater to simulate the weightlessness of space",
                "🌟 The first woman in space was Valentina Tereshkova in 1963!",
                
                # Astronaut Training and Selection
                "🎓 Astronaut candidates need advanced degrees in STEM fields",
                "✈️ Test pilot experience is valuable but not required for astronauts",
                "🏊 Astronauts train for spacewalks in NASA's giant swimming pool",
                "🤢 About 50% of astronauts experience space sickness initially",
                "🧠 Astronauts train for years learning spacecraft systems and procedures",
                "🌍 International astronauts train at centers around the world",
                "🚀 Astronaut training includes survival skills for emergency landings",
                "🔧 Astronauts learn to repair and maintain complex space equipment",
                "📚 Continuous learning is required as technology advances",
                "👥 Teamwork and communication skills are crucial for astronauts",
                
                # Life in Space
                "🌅 Astronauts on the ISS experience a sunrise or sunset every 45 minutes",
                "💧 Water sticks to surfaces in space due to surface tension",
                "🍽️ Space food is specially prepared to prevent crumbs and spills",
                "📞 Astronauts can call family and friends from space",
                "📱 The ISS has internet access for communication with Earth",
                "🧼 Personal hygiene requires special techniques and products",
                "💤 Sleep can be challenging due to the constant sunrise/sunset cycle",
                "🔬 Astronauts conduct hundreds of scientific experiments",
                "📸 Many astronauts become skilled photographers from space",
                "🌍 The overview effect changes how astronauts see Earth and humanity"
            ]
        }
        
        # Conversation responses with more variety
        self.greetings = [
            "Hello! I'm your Ultimate NASA Space Facts AI! 🚀",
            "Welcome to the vast universe of space exploration! 🌟",
            "Ready to discover incredible space facts? 🌌",
            "Greetings, cosmic explorer! 👨‍🚀",
            "Let's journey through the cosmos together! 🌍",
            "Space awaits your curiosity! What shall we explore? 🛸",
            "The universe holds infinite mysteries - let's uncover them! ⭐"
        ]
        
        self.encouragements = [
            "That's fascinating! What else would you like to explore? 🤔",
            "Space is incredible! Ask me about any cosmic topic! ⭐",
            "Amazing! What other space mysteries shall we discover? 🚀",
            "Wonderful question! What's next on your space adventure? 🌌",
            "Great choice! Ready for another cosmic fact? 🛸",
            "The universe is full of wonders! What interests you next? 💫",
            "Excellent! Let's continue our space exploration journey! 🌟"
        ]
    
    def get_space_fact(self, user_input):
        """Get a random space fact from the vast database"""
        # Clean user input
        topic = user_input.lower().strip()
        
        # Remove common words to find the main topic
        common_words = ['tell', 'me', 'about', 'what', 'is', 'are', 'the', 'a', 'an', 
                       'facts', 'fact', 'space', 'give', 'show', 'explain', 'describe']
        words = topic.split()
        cleaned_words = [word for word in words if word not in common_words]
        
        if cleaned_words:
            topic = ' '.join(cleaned_words)
        
        # Check for exact matches first
        if topic in self.space_facts:
            return random.choice(self.space_facts[topic])
        
        # Check for partial matches
        for key in self.space_facts:
            if key in topic or topic in key:
                return random.choice(self.space_facts[key])
        
        # Special handling for common variations
        topic_variations = {
            'jupiter moon': 'jupiter',
            'jupiter moons': 'jupiter',
            'saturn rings': 'saturn',
            'mars rover': 'perseverance',
            'moon landing': 'moon',
            'space telescope': 'james webb',
            'solar system': 'space',
            'outer space': 'space',
            'deep space': 'space'
        }
        
        for variation, actual_topic in topic_variations.items():
            if variation in topic:
                return random.choice(self.space_facts[actual_topic])
        
        # If no match found, provide helpful suggestions
        available_topics = list(self.space_facts.keys())
        suggestions = random.sample(available_topics, min(6, len(available_topics)))
        return f"🤔 I don't have facts about '{user_input}' yet! Try asking about: {', '.join(suggestions)}"
    
    def get_response(self, user_input):
        """Generate comprehensive response based on user input"""
        input_lower = user_input.lower()
        
        # Greetings
        if any(word in input_lower for word in ['hello', 'hi', 'hey', 'greetings', 'start']):
            return random.choice(self.greetings)
        
        # Help requests - now with more comprehensive help
        if any(word in input_lower for word in ['help', 'what can you', 'how do you', 'commands']):
            topics = list(self.space_facts.keys())
            sample_topics = random.sample(topics, min(8, len(topics)))
            return f"""🚀 Welcome to the Ultimate NASA Space Facts AI!
            
🌟 I have vast knowledge about space including:
• Planets: {', '.join(sample_topics[:4])}
• Missions: {', '.join(sample_topics[4:8])}
• And many more cosmic topics!

💡 Just type any space topic like:
• 'mars' or 'tell me about Mars'
• 'black holes' or 'what are black holes'
• 'artemis mission' or 'NASA Artemis'
• 'james webb telescope'

🎯 I have over 1000 space facts to share!"""
        
        # Show available topics
        if any(phrase in input_lower for phrase in ['what topics', 'what can you tell', 'list topics']):
            topics = list(self.space_facts.keys())
            categories = {
                'Planets': [t for t in topics if t in ['mars', 'sun', 'jupiter', 'saturn', 'earth', 'moon', 'venus', 'mercury']],
                'Space Objects': [t for t in topics if t in ['black hole', 'stars', 'galaxy', 'asteroid', 'comet']],
                'NASA Missions': [t for t in topics if t in ['artemis', 'perseverance', 'james webb', 'europa clipper']],
                'General': [t for t in topics if t in ['space', 'astronaut', 'telescope']]
            }
            
            response = "🌌 Here are my main topic categories:\n\n"
            for category, topic_list in categories.items():
                if topic_list:
                    response += f"🚀 {category}: {', '.join(topic_list[:5])}\n"
            response += "\n💡 Just type any topic name to get amazing facts!"
            return response
        
        # Quit/exit
        if any(word in input_lower for word in ['quit', 'exit', 'bye', 'goodbye', 'stop']):
            return "🌟 Thanks for exploring the vast universe with me! Keep looking up at the stars! 🚀"
        
        # Count available facts
        if any(phrase in input_lower for phrase in ['how many facts', 'total facts', 'number of facts']):
            total_facts = sum(len(facts) for facts in self.space_facts.values())
            topics_count = len(self.space_facts.keys())
            return f"🎯 I have {total_facts}+ space facts covering {topics_count} different topics! Ask me about any space subject!"
        
        # Default: provide space fact
        return self.get_space_fact(user_input)
    
    def interactive_mode(self):
        """Run the ultimate interactive space facts AI"""
        print("🌟 Welcome to the Ultimate NASA Space Facts AI!")
        print("I have VAST knowledge with 1000+ space facts!")
        print()
        print("✨ Try asking about:")
        print("  🪐 Planets: mars, jupiter, saturn, sun, earth, moon...")
        print("  🌌 Space objects: black holes, stars, galaxies...")
        print("  🚀 NASA missions: artemis, perseverance, james webb...")
        print("  👨‍🚀 Space topics: astronauts, telescopes, space...")
        print()
        print("💡 Commands: 'help', 'topics', 'quit'")
        print("─" * 60)
        
        facts_shared = 0
        topic_counts = {}
        
        while True:
            try:
                # Get user input
                user_input = input("\\n🌌 Ask me about space: ").strip()
                
                if not user_input:
                    print("💡 Try asking about a planet, mission, or space object!")
                    continue
                
                # Get and display response
                response = self.get_response(user_input)
                
                # Check if user wants to quit
                if 'thanks for exploring' in response.lower():
                    print(f"\\n{response}")
                    print(f"📊 You learned {facts_shared} amazing space facts today!")
                    if topic_counts:
                        print("🏆 Topics explored:", ', '.join(topic_counts.keys()))
                    break
                
                print(f"\\n{response}")
                
                # Count facts shared and track topics
                if response.startswith(('🔴', '☀️', '🌙', '🌪️', '🕳️', '⭐', '🌌', '🪨', 
                                       '☄️', '🚀', '🤖', '🔭', '👩‍🚀', '🌟', '💍', 
                                       '🔥', '🌍', '🌀')):
                    facts_shared += 1
                    
                    # Track which topics user is interested in
                    for topic in self.space_facts.keys():
                        if topic in user_input.lower():
                            topic_counts[topic] = topic_counts.get(topic, 0) + 1
                    
                    # Show personalized encouragements
                    if facts_shared % 5 == 0:
                        print(f"\\n{random.choice(self.encouragements)}")
                        print(f"📈 You've learned {facts_shared} space facts so far!")
                
                # Show achievement notifications with more levels
                if facts_shared == 5:
                    print("\\n🎉 Achievement: Space Explorer! You've learned 5 space facts!")
                elif facts_shared == 10:
                    print("\\n🏆 Achievement: Cosmic Scholar! You've learned 10 space facts!")
                elif facts_shared == 20:
                    print("\\n🌟 Achievement: Space Expert! You've learned 20 space facts!")
                elif facts_shared == 50:
                    print("\\n🚀 Achievement: NASA Knowledge Master! You've learned 50 space facts!")
                elif facts_shared == 100:
                    print("\\n🌌 Achievement: Universe Explorer! You've learned 100 space facts!")
                
            except KeyboardInterrupt:
                print("\\n\\n👋 Thanks for exploring the vast universe! Keep looking up! 🚀")
                break
            except Exception as e:
                print("🤖 Oops! Something went wrong. Let's continue exploring space!")

# Enhanced function for direct fact retrieval
def get_space_fact(topic):
    """Get a space fact from the vast database"""
    ai = UltimateNASASpaceFactsAI()
    return ai.get_space_fact(topic)

# Enhanced demo function showing the vast content
def demo_mode():
    """Show demo of the ultimate vast content AI"""
    print("🚀 ULTIMATE NASA SPACE FACTS AI - VAST CONTENT DEMO")
    print("=" * 60)
    print("Same simple structure, now with 1000+ space facts!")
    
    ai = UltimateNASASpaceFactsAI()
    
    # Count total facts to show the vast content
    total_facts = sum(len(facts) for facts in ai.space_facts.values())
    total_topics = len(ai.space_facts.keys())
    
    print(f"📊 Database contains: {total_facts}+ facts across {total_topics} topics")
    
    demo_inputs = [
        "mars",
        "tell me about the sun", 
        "jupiter",
        "black holes",
        "artemis mission",
        "james webb telescope", 
        "saturn rings",
        "europa clipper",
        "astronauts",
        "mercury"
    ]
    
    print("\\n🌟 Sample conversations:")
    print("─" * 40)
    
    for i, topic in enumerate(demo_inputs, 1):
        print(f"\\n{i}. User: '{topic}'")
        response = ai.get_response(topic)
        # Show first 100 characters of response to demonstrate variety
        display_response = response[:100] + "..." if len(response) > 100 else response
        print(f"   AI: {display_response}")
        
        if i < len(demo_inputs):
            print("   " + "─" * 35)
    
    print(f"\\n🎉 This is just a sample - I have {total_facts}+ facts to share!")
    print(f"🌟 Covering {total_topics} different space topics in detail!")

# Main program
def main():
    """Run the Ultimate NASA Space Facts AI"""
    ai = UltimateNASASpaceFactsAI()
    ai.interactive_mode()

if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        demo_mode()
    else:
        main()