import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import random
import string

API_CURRENCIES = "https://ntcdl0i.com/api/v1/currencies.json"
API_COUNTRIES  = "https://ntcdl0i.com/api/v1/countries.json"
API_REGISTER   = "https://ntcdl0i.com/api/v1/external-register-email.json"
API_USER       = "https://ntcdl0i.com/api/v1/user.json"

# ✅ ISO таблица из ресурса UPS (сокращённо, добавь другие по этому формату)
ISO_COUNTRY_TABLE = [
  {
    "country_name": "Afghanistan",
    "iso_country_code": "AF",
    "iso_currency_code": "AFN",
    "currency_name": "Afghan afghani"
  },
  {
    "country_name": "Åland Islands",
    "iso_country_code": "AX",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Albania",
    "iso_country_code": "AL",
    "iso_currency_code": "ALL",
    "currency_name": "Albanian lek"
  },
  {
    "country_name": "Algeria",
    "iso_country_code": "DZ",
    "iso_currency_code": "DZD",
    "currency_name": "Algerian dinar"
  },
  {
    "country_name": "American Samoa",
    "iso_country_code": "AS",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Andorra",
    "iso_country_code": "AD",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Angola",
    "iso_country_code": "AO",
    "iso_currency_code": "AOA",
    "currency_name": "Angolan kwanza"
  },
  {
    "country_name": "Anguilla",
    "iso_country_code": "AI",
    "iso_currency_code": "XCD",
    "currency_name": "East Caribbean dollar"
  },
  {
    "country_name": "Antigua and Barbuda",
    "iso_country_code": "AG",
    "iso_currency_code": "XCD",
    "currency_name": "East Caribbean dollar"
  },
  {
    "country_name": "Argentina",
    "iso_country_code": "AR",
    "iso_currency_code": "ARS",
    "currency_name": "Argentine peso"
  },
  {
    "country_name": "Armenia",
    "iso_country_code": "AM",
    "iso_currency_code": "AMD",
    "currency_name": "Armenian dram"
  },
  {
    "country_name": "Aruba",
    "iso_country_code": "AW",
    "iso_currency_code": "AWG",
    "currency_name": "Aruban florin"
  },
  {
    "country_name": "Australia",
    "iso_country_code": "AU",
    "iso_currency_code": "AUD",
    "currency_name": "Australian dollar"
  },
  {
    "country_name": "Austria",
    "iso_country_code": "AT",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Azerbaijan",
    "iso_country_code": "AZ",
    "iso_currency_code": "AZN",
    "currency_name": "Azerbaijani manat"
  },
  {
    "country_name": "Bahamas",
    "iso_country_code": "BS",
    "iso_currency_code": "BSD",
    "currency_name": "Bahamian dollar"
  },
  {
    "country_name": "Bahrain",
    "iso_country_code": "BH",
    "iso_currency_code": "BHD",
    "currency_name": "Bahraini dinar"
  },
  {
    "country_name": "Bangladesh",
    "iso_country_code": "BD",
    "iso_currency_code": "BDT",
    "currency_name": "Bangladeshi taka"
  },
  {
    "country_name": "Barbados",
    "iso_country_code": "BB",
    "iso_currency_code": "BBD",
    "currency_name": "Barbadian dollar"
  },
  {
    "country_name": "Belarus",
    "iso_country_code": "BY",
    "iso_currency_code": "BYN",
    "currency_name": "Belarusian ruble"
  },
  {
    "country_name": "Belgium",
    "iso_country_code": "BE",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Belize",
    "iso_country_code": "BZ",
    "iso_currency_code": "BZD",
    "currency_name": "Belize dollar"
  },
  {
    "country_name": "Benin",
    "iso_country_code": "BJ",
    "iso_currency_code": "XOF",
    "currency_name": "West African CFA franc"
  },
  {
    "country_name": "Bermuda",
    "iso_country_code": "BM",
    "iso_currency_code": "BMD",
    "currency_name": "Bermudian dollar"
  },
  {
    "country_name": "Bhutan",
    "iso_country_code": "BT",
    "iso_currency_code": "BTN",
    "currency_name": "Bhutanese ngultrum"
  },
  {
    "country_name": "Bolivia",
    "iso_country_code": "BO",
    "iso_currency_code": "BOB",
    "currency_name": "Bolivian boliviano"
  },
  {
    "country_name": "Bonaire, Sint Eustatius and Saba",
    "iso_country_code": "BQ",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Bosnia and Herzegovina",
    "iso_country_code": "BA",
    "iso_currency_code": "BAM",
    "currency_name": "Bosnia and Herzegovina convertible mark"
  },
  {
    "country_name": "Botswana",
    "iso_country_code": "BW",
    "iso_currency_code": "BWP",
    "currency_name": "Botswana pula"
  },
  {
    "country_name": "Bouvet Island",
    "iso_country_code": "BV",
    "iso_currency_code": "NOK",
    "currency_name": "Norwegian krone"
  },
  {
    "country_name": "Brazil",
    "iso_country_code": "BR",
    "iso_currency_code": "BRL",
    "currency_name": "Brazilian real"
  },
  {
    "country_name": "British Indian Ocean Territory",
    "iso_country_code": "IO",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Brunei Darussalam",
    "iso_country_code": "BN",
    "iso_currency_code": "BND",
    "currency_name": "Brunei dollar"
  },
  {
    "country_name": "Bulgaria",
    "iso_country_code": "BG",
    "iso_currency_code": "BGN",
    "currency_name": "Bulgarian lev"
  },
  {
    "country_name": "Burkina Faso",
    "iso_country_code": "BF",
    "iso_currency_code": "XOF",
    "currency_name": "West African CFA franc"
  },
  {
    "country_name": "Burundi",
    "iso_country_code": "BI",
    "iso_currency_code": "BIF",
    "currency_name": "Burundian franc"
  },
  {
    "country_name": "Cabo Verde",
    "iso_country_code": "CV",
    "iso_currency_code": "CVE",
    "currency_name": "Cape Verdean escudo"
  },
  {
    "country_name": "Cambodia",
    "iso_country_code": "KH",
    "iso_currency_code": "KHR",
    "currency_name": "Cambodian riel"
  },
  {
    "country_name": "Cameroon",
    "iso_country_code": "CM",
    "iso_currency_code": "XAF",
    "currency_name": "Central African CFA franc"
  },
  {
    "country_name": "Canada",
    "iso_country_code": "CA",
    "iso_currency_code": "CAD",
    "currency_name": "Canadian dollar"
  },
  {
    "country_name": "Cayman Islands",
    "iso_country_code": "KY",
    "iso_currency_code": "KYD",
    "currency_name": "Cayman Islands dollar"
  },
  {
    "country_name": "Central African Republic",
    "iso_country_code": "CF",
    "iso_currency_code": "XAF",
    "currency_name": "Central African CFA franc"
  },
  {
    "country_name": "Chad",
    "iso_country_code": "TD",
    "iso_currency_code": "XAF",
    "currency_name": "Central African CFA franc"
  },
  {
    "country_name": "Chile",
    "iso_country_code": "CL",
    "iso_currency_code": "CLP",
    "currency_name": "Chilean peso"
  },
  {
    "country_name": "China",
    "iso_country_code": "CN",
    "iso_currency_code": "CNY",
    "currency_name": "Chinese yuan"
  },
  {
    "country_name": "Christmas Island",
    "iso_country_code": "CX",
    "iso_currency_code": "AUD",
    "currency_name": "Australian dollar"
  },
  {
    "country_name": "Cocos (Keeling) Islands",
    "iso_country_code": "CC",
    "iso_currency_code": "AUD",
    "currency_name": "Australian dollar"
  },
  {
    "country_name": "Colombia",
    "iso_country_code": "CO",
    "iso_currency_code": "COP",
    "currency_name": "Colombian peso"
  },
  {
    "country_name": "Comoros",
    "iso_country_code": "KM",
    "iso_currency_code": "KMF",
    "currency_name": "Comorian franc"
  },
  {
    "country_name": "Congo",
    "iso_country_code": "CG",
    "iso_currency_code": "XAF",
    "currency_name": "Central African CFA franc"
  },
  {
    "country_name": "Congo (Democratic Republic)",
    "iso_country_code": "CD",
    "iso_currency_code": "CDF",
    "currency_name": "Congolese franc"
  },
  {
    "country_name": "Cook Islands",
    "iso_country_code": "CK",
    "iso_currency_code": "NZD",
    "currency_name": "New Zealand dollar"
  },
  {
    "country_name": "Costa Rica",
    "iso_country_code": "CR",
    "iso_currency_code": "CRC",
    "currency_name": "Costa Rican colón"
  },
  {
    "country_name": "Côte d'Ivoire",
    "iso_country_code": "CI",
    "iso_currency_code": "XOF",
    "currency_name": "West African CFA franc"
  },
  {
    "country_name": "Croatia",
    "iso_country_code": "HR",
    "iso_currency_code": "HRK",
    "currency_name": "Croatian kuna"
  },
  {
    "country_name": "Cuba",
    "iso_country_code": "CU",
    "iso_currency_code": "CUP",
    "currency_name": "Cuban peso"
  },
  {
    "country_name": "Curaçao",
    "iso_country_code": "CW",
    "iso_currency_code": "ANG",
    "currency_name": "Netherlands Antillean guilder"
  },
  {
    "country_name": "Cyprus",
    "iso_country_code": "CY",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Czech Republic",
    "iso_country_code": "CZ",
    "iso_currency_code": "CZK",
    "currency_name": "Czech koruna"
  },
  {
    "country_name": "Denmark",
    "iso_country_code": "DK",
    "iso_currency_code": "DKK",
    "currency_name": "Danish krone"
  },
  {
    "country_name": "Djibouti",
    "iso_country_code": "DJ",
    "iso_currency_code": "DJF",
    "currency_name": "Djiboutian franc"
  },
  {
    "country_name": "Dominica",
    "iso_country_code": "DM",
    "iso_currency_code": "XCD",
    "currency_name": "East Caribbean dollar"
  },
  {
    "country_name": "Dominican Republic",
    "iso_country_code": "DO",
    "iso_currency_code": "DOP",
    "currency_name": "Dominican peso"
  },
  {
    "country_name": "Ecuador",
    "iso_country_code": "EC",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Egypt",
    "iso_country_code": "EG",
    "iso_currency_code": "EGP",
    "currency_name": "Egyptian pound"
  },
  {
    "country_name": "El Salvador",
    "iso_country_code": "SV",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Equatorial Guinea",
    "iso_country_code": "GQ",
    "iso_currency_code": "XAF",
    "currency_name": "Central African CFA franc"
  },
  {
    "country_name": "Eritrea",
    "iso_country_code": "ER",
    "iso_currency_code": "ERN",
    "currency_name": "Eritrean nakfa"
  },
  {
    "country_name": "Estonia",
    "iso_country_code": "EE",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Eswatini",
    "iso_country_code": "SZ",
    "iso_currency_code": "SZL",
    "currency_name": "Swazi lilangeni"
  },
  {
    "country_name": "Ethiopia",
    "iso_country_code": "ET",
    "iso_currency_code": "ETB",
    "currency_name": "Ethiopian birr"
  },
  {
    "country_name": "Falkland Islands",
    "iso_country_code": "FK",
    "iso_currency_code": "FKP",
    "currency_name": "Falkland Islands pound"
  },
  {
    "country_name": "Faroe Islands",
    "iso_country_code": "FO",
    "iso_currency_code": "DKK",
    "currency_name": "Danish krone"
  },
  {
    "country_name": "Fiji",
    "iso_country_code": "FJ",
    "iso_currency_code": "FJD",
    "currency_name": "Fijian dollar"
  },
  {
    "country_name": "Finland",
    "iso_country_code": "FI",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "France",
    "iso_country_code": "FR",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "French Guiana",
    "iso_country_code": "GF",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "French Polynesia",
    "iso_country_code": "PF",
    "iso_currency_code": "XPF",
    "currency_name": "CFP franc"
  },
  {
    "country_name": "French Southern Territories",
    "iso_country_code": "TF",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Gabon",
    "iso_country_code": "GA",
    "iso_currency_code": "XAF",
    "currency_name": "Central African CFA franc"
  },
  {
    "country_name": "Gambia",
    "iso_country_code": "GM",
    "iso_currency_code": "GMD",
    "currency_name": "Gambian dalasi"
  },
  {
    "country_name": "Georgia",
    "iso_country_code": "GE",
    "iso_currency_code": "GEL",
    "currency_name": "Georgian lari"
  },
  {
    "country_name": "Germany",
    "iso_country_code": "DE",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Ghana",
    "iso_country_code": "GH",
    "iso_currency_code": "GHS",
    "currency_name": "Ghanaian cedi"
  },
  {
    "country_name": "Gibraltar",
    "iso_country_code": "GI",
    "iso_currency_code": "GIP",
    "currency_name": "Gibraltar pound"
  },
  {
    "country_name": "Greece",
    "iso_country_code": "GR",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Greenland",
    "iso_country_code": "GL",
    "iso_currency_code": "DKK",
    "currency_name": "Danish krone"
  },
  {
    "country_name": "Grenada",
    "iso_country_code": "GD",
    "iso_currency_code": "XCD",
    "currency_name": "East Caribbean dollar"
  },
  {
    "country_name": "Guadeloupe",
    "iso_country_code": "GP",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Guam",
    "iso_country_code": "GU",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Guatemala",
    "iso_country_code": "GT",
    "iso_currency_code": "GTQ",
    "currency_name": "Guatemalan quetzal"
  },
  {
    "country_name": "Guernsey",
    "iso_country_code": "GG",
    "iso_currency_code": "GBP",
    "currency_name": "British pound"
  },
  {
    "country_name": "Guinea",
    "iso_country_code": "GN",
    "iso_currency_code": "GNF",
    "currency_name": "Guinean franc"
  },
  {
    "country_name": "Guinea-Bissau",
    "iso_country_code": "GW",
    "iso_currency_code": "XOF",
    "currency_name": "West African CFA franc"
  },
  {
    "country_name": "Guyana",
    "iso_country_code": "GY",
    "iso_currency_code": "GYD",
    "currency_name": "Guyanese dollar"
  },
  {
    "country_name": "Haiti",
    "iso_country_code": "HT",
    "iso_currency_code": "HTG",
    "currency_name": "Haitian gourde"
  },
  {
    "country_name": "Heard Island and McDonald Islands",
    "iso_country_code": "HM",
    "iso_currency_code": "AUD",
    "currency_name": "Australian dollar"
  },
  {
    "country_name": "Holy See",
    "iso_country_code": "VA",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Honduras",
    "iso_country_code": "HN",
    "iso_currency_code": "HNL",
    "currency_name": "Honduran lempira"
  },
  {
    "country_name": "Hong Kong",
    "iso_country_code": "HK",
    "iso_currency_code": "HKD",
    "currency_name": "Hong Kong dollar"
  },
  {
    "country_name": "Hungary",
    "iso_country_code": "HU",
    "iso_currency_code": "HUF",
    "currency_name": "Hungarian forint"
  },
  {
    "country_name": "Iceland",
    "iso_country_code": "IS",
    "iso_currency_code": "ISK",
    "currency_name": "Icelandic króna"
  },
  {
    "country_name": "India",
    "iso_country_code": "IN",
    "iso_currency_code": "INR",
    "currency_name": "Indian rupee"
  },
  {
    "country_name": "Indonesia",
    "iso_country_code": "ID",
    "iso_currency_code": "IDR",
    "currency_name": "Indonesian rupiah"
  },
  {
    "country_name": "Iran",
    "iso_country_code": "IR",
    "iso_currency_code": "IRR",
    "currency_name": "Iranian rial"
  },
  {
    "country_name": "Iraq",
    "iso_country_code": "IQ",
    "iso_currency_code": "IQD",
    "currency_name": "Iraqi dinar"
  },
  {
    "country_name": "Ireland",
    "iso_country_code": "IE",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Isle of Man",
    "iso_country_code": "IM",
    "iso_currency_code": "GBP",
    "currency_name": "British pound"
  },
  {
    "country_name": "Israel",
    "iso_country_code": "IL",
    "iso_currency_code": "ILS",
    "currency_name": "Israeli new shekel"
  },
  {
    "country_name": "Italy",
    "iso_country_code": "IT",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Jamaica",
    "iso_country_code": "JM",
    "iso_currency_code": "JMD",
    "currency_name": "Jamaican dollar"
  },
  {
    "country_name": "Japan",
    "iso_country_code": "JP",
    "iso_currency_code": "JPY",
    "currency_name": "Japanese yen"
  },
  {
    "country_name": "Jersey",
    "iso_country_code": "JE",
    "iso_currency_code": "GBP",
    "currency_name": "British pound"
  },
  {
    "country_name": "Jordan",
    "iso_country_code": "JO",
    "iso_currency_code": "JOD",
    "currency_name": "Jordanian dinar"
  },
  {
    "country_name": "Kazakhstan",
    "iso_country_code": "KZ",
    "iso_currency_code": "KZT",
    "currency_name": "Kazakhstani tenge"
  },
  {
    "country_name": "Kenya",
    "iso_country_code": "KE",
    "iso_currency_code": "KES",
    "currency_name": "Kenyan shilling"
  },
  {
    "country_name": "Kiribati",
    "iso_country_code": "KI",
    "iso_currency_code": "AUD",
    "currency_name": "Australian dollar"
  },
  {
    "country_name": "Korea (North)",
    "iso_country_code": "KP",
    "iso_currency_code": "KPW",
    "currency_name": "North Korean won"
  },
  {
    "country_name": "Korea (South)",
    "iso_country_code": "KR",
    "iso_currency_code": "KRW",
    "currency_name": "South Korean won"
  },
  {
    "country_name": "Kuwait",
    "iso_country_code": "KW",
    "iso_currency_code": "KWD",
    "currency_name": "Kuwaiti dinar"
  },
  {
    "country_name": "Kyrgyzstan",
    "iso_country_code": "KG",
    "iso_currency_code": "KGS",
    "currency_name": "Kyrgyzstani som"
  },
  {
    "country_name": "Lao People's Democratic Republic",
    "iso_country_code": "LA",
    "iso_currency_code": "LAK",
    "currency_name": "Lao kip"
  },
  {
    "country_name": "Latvia",
    "iso_country_code": "LV",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Lebanon",
    "iso_country_code": "LB",
    "iso_currency_code": "LBP",
    "currency_name": "Lebanese pound"
  },
  {
    "country_name": "Lesotho",
    "iso_country_code": "LS",
    "iso_currency_code": "LSL",
    "currency_name": "Lesotho loti"
  },
  {
    "country_name": "Liberia",
    "iso_country_code": "LR",
    "iso_currency_code": "LRD",
    "currency_name": "Liberian dollar"
  },
  {
    "country_name": "Libya",
    "iso_country_code": "LY",
    "iso_currency_code": "LYD",
    "currency_name": "Libyan dinar"
  },
  {
    "country_name": "Liechtenstein",
    "iso_country_code": "LI",
    "iso_currency_code": "CHF",
    "currency_name": "Swiss franc"
  },
  {
    "country_name": "Lithuania",
    "iso_country_code": "LT",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Luxembourg",
    "iso_country_code": "LU",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Macao",
    "iso_country_code": "MO",
    "iso_currency_code": "MOP",
    "currency_name": "Macanese pataca"
  },
  {
    "country_name": "Madagascar",
    "iso_country_code": "MG",
    "iso_currency_code": "MGA",
    "currency_name": "Malagasy ariary"
  },
  {
    "country_name": "Malawi",
    "iso_country_code": "MW",
    "iso_currency_code": "MWK",
    "currency_name": "Malawian kwacha"
  },
  {
    "country_name": "Malaysia",
    "iso_country_code": "MY",
    "iso_currency_code": "MYR",
    "currency_name": "Malaysian ringgit"
  },
  {
    "country_name": "Maldives",
    "iso_country_code": "MV",
    "iso_currency_code": "MVR",
    "currency_name": "Maldivian rufiyaa"
  },
  {
    "country_name": "Mali",
    "iso_country_code": "ML",
    "iso_currency_code": "XOF",
    "currency_name": "West African CFA franc"
  },
  {
    "country_name": "Malta",
    "iso_country_code": "MT",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Marshall Islands",
    "iso_country_code": "MH",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Martinique",
    "iso_country_code": "MQ",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Mauritania",
    "iso_country_code": "MR",
    "iso_currency_code": "MRU",
    "currency_name": "Mauritanian ouguiya"
  },
  {
    "country_name": "Mauritius",
    "iso_country_code": "MU",
    "iso_currency_code": "MUR",
    "currency_name": "Mauritian rupee"
  },
  {
    "country_name": "Mayotte",
    "iso_country_code": "YT",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Mexico",
    "iso_country_code": "MX",
    "iso_currency_code": "MXN",
    "currency_name": "Mexican peso"
  },
  {
    "country_name": "Micronesia",
    "iso_country_code": "FM",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Moldova",
    "iso_country_code": "MD",
    "iso_currency_code": "MDL",
    "currency_name": "Moldovan leu"
  },
  {
    "country_name": "Monaco",
    "iso_country_code": "MC",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Mongolia",
    "iso_country_code": "MN",
    "iso_currency_code": "MNT",
    "currency_name": "Mongolian tögrög"
  },
  {
    "country_name": "Montenegro",
    "iso_country_code": "ME",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Montserrat",
    "iso_country_code": "MS",
    "iso_currency_code": "XCD",
    "currency_name": "East Caribbean dollar"
  },
  {
    "country_name": "Morocco",
    "iso_country_code": "MA",
    "iso_currency_code": "MAD",
    "currency_name": "Moroccan dirham"
  },
  {
    "country_name": "Mozambique",
    "iso_country_code": "MZ",
    "iso_currency_code": "MZN",
    "currency_name": "Mozambican metical"
  },
  {
    "country_name": "Myanmar",
    "iso_country_code": "MM",
    "iso_currency_code": "MMK",
    "currency_name": "Burmese kyat"
  },
  {
    "country_name": "Namibia",
    "iso_country_code": "NA",
    "iso_currency_code": "NAD",
    "currency_name": "Namibian dollar"
  },
  {
    "country_name": "Nauru",
    "iso_country_code": "NR",
    "iso_currency_code": "AUD",
    "currency_name": "Australian dollar"
  },
  {
    "country_name": "Nepal",
    "iso_country_code": "NP",
    "iso_currency_code": "NPR",
    "currency_name": "Nepalese rupee"
  },
  {
    "country_name": "Netherlands",
    "iso_country_code": "NL",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "New Caledonia",
    "iso_country_code": "NC",
    "iso_currency_code": "XPF",
    "currency_name": "CFP franc"
  },
  {
    "country_name": "New Zealand",
    "iso_country_code": "NZ",
    "iso_currency_code": "NZD",
    "currency_name": "New Zealand dollar"
  },
  {
    "country_name": "Nicaragua",
    "iso_country_code": "NI",
    "iso_currency_code": "NIO",
    "currency_name": "Nicaraguan córdoba"
  },
  {
    "country_name": "Niger",
    "iso_country_code": "NE",
    "iso_currency_code": "XOF",
    "currency_name": "West African CFA franc"
  },
  {
    "country_name": "Nigeria",
    "iso_country_code": "NG",
    "iso_currency_code": "NGN",
    "currency_name": "Nigerian naira"
  },
  {
    "country_name": "Niue",
    "iso_country_code": "NU",
    "iso_currency_code": "NZD",
    "currency_name": "New Zealand dollar"
  },
  {
    "country_name": "Norfolk Island",
    "iso_country_code": "NF",
    "iso_currency_code": "AUD",
    "currency_name": "Australian dollar"
  },
  {
    "country_name": "North Macedonia",
    "iso_country_code": "MK",
    "iso_currency_code": "MKD",
    "currency_name": "Macedonian denar"
  },
  {
    "country_name": "Northern Mariana Islands",
    "iso_country_code": "MP",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Norway",
    "iso_country_code": "NO",
    "iso_currency_code": "NOK",
    "currency_name": "Norwegian krone"
  },
  {
    "country_name": "Oman",
    "iso_country_code": "OM",
    "iso_currency_code": "OMR",
    "currency_name": "Omani rial"
  },
  {
    "country_name": "Pakistan",
    "iso_country_code": "PK",
    "iso_currency_code": "PKR",
    "currency_name": "Pakistani rupee"
  },
  {
    "country_name": "Palau",
    "iso_country_code": "PW",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Panama",
    "iso_country_code": "PA",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Papua New Guinea",
    "iso_country_code": "PG",
    "iso_currency_code": "PGK",
    "currency_name": "Papua New Guinean kina"
  },
  {
    "country_name": "Paraguay",
    "iso_country_code": "PY",
    "iso_currency_code": "PYG",
    "currency_name": "Paraguayan guaraní"
  },
  {
    "country_name": "Peru",
    "iso_country_code": "PE",
    "iso_currency_code": "PEN",
    "currency_name": "Peruvian sol"
  },
  {
    "country_name": "Philippines",
    "iso_country_code": "PH",
    "iso_currency_code": "PHP",
    "currency_name": "Philippine peso"
  },
  {
    "country_name": "Pitcairn",
    "iso_country_code": "PN",
    "iso_currency_code": "NZD",
    "currency_name": "New Zealand dollar"
  },
  {
    "country_name": "Poland",
    "iso_country_code": "PL",
    "iso_currency_code": "PLN",
    "currency_name": "Polish złoty"
  },
  {
    "country_name": "Portugal",
    "iso_country_code": "PT",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Puerto Rico",
    "iso_country_code": "PR",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Qatar",
    "iso_country_code": "QA",
    "iso_currency_code": "QAR",
    "currency_name": "Qatari riyal"
  },
  {
    "country_name": "Réunion",
    "iso_country_code": "RE",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Romania",
    "iso_country_code": "RO",
    "iso_currency_code": "RON",
    "currency_name": "Romanian leu"
  },
  {
    "country_name": "Russia",
    "iso_country_code": "RU",
    "iso_currency_code": "RUB",
    "currency_name": "Russian ruble"
  },
  {
    "country_name": "Rwanda",
    "iso_country_code": "RW",
    "iso_currency_code": "RWF",
    "currency_name": "Rwandan franc"
  },
  {
    "country_name": "Saint Barthélemy",
    "iso_country_code": "BL",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Saint Helena, Ascension and Tristan da Cunha",
    "iso_country_code": "SH",
    "iso_currency_code": "SHP",
    "currency_name": "Saint Helena pound"
  },
  {
    "country_name": "Saint Kitts and Nevis",
    "iso_country_code": "KN",
    "iso_currency_code": "XCD",
    "currency_name": "East Caribbean dollar"
  },
  {
    "country_name": "Saint Lucia",
    "iso_country_code": "LC",
    "iso_currency_code": "XCD",
    "currency_name": "East Caribbean dollar"
  },
  {
    "country_name": "Saint Martin",
    "iso_country_code": "MF",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Saint Pierre and Miquelon",
    "iso_country_code": "PM",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Saint Vincent and the Grenadines",
    "iso_country_code": "VC",
    "iso_currency_code": "XCD",
    "currency_name": "East Caribbean dollar"
  },
  {
    "country_name": "Samoa",
    "iso_country_code": "WS",
    "iso_currency_code": "WST",
    "currency_name": "Samoan tālā"
  },
  {
    "country_name": "San Marino",
    "iso_country_code": "SM",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Sao Tome and Principe",
    "iso_country_code": "ST",
    "iso_currency_code": "STN",
    "currency_name": "São Tomé and Príncipe dobra"
  },
  {
    "country_name": "Saudi Arabia",
    "iso_country_code": "SA",
    "iso_currency_code": "SAR",
    "currency_name": "Saudi riyal"
  },
  {
    "country_name": "Senegal",
    "iso_country_code": "SN",
    "iso_currency_code": "XOF",
    "currency_name": "West African CFA franc"
  },
  {
    "country_name": "Serbia",
    "iso_country_code": "RS",
    "iso_currency_code": "RSD",
    "currency_name": "Serbian dinar"
  },
  {
    "country_name": "Seychelles",
    "iso_country_code": "SC",
    "iso_currency_code": "SCR",
    "currency_name": "Seychellois rupee"
  },
  {
    "country_name": "Sierra Leone",
    "iso_country_code": "SL",
    "iso_currency_code": "SLE",
    "currency_name": "Sierra Leonean leone"
  },
  {
    "country_name": "Singapore",
    "iso_country_code": "SG",
    "iso_currency_code": "SGD",
    "currency_name": "Singapore dollar"
  },
  {
    "country_name": "Sint Maarten",
    "iso_country_code": "SX",
    "iso_currency_code": "ANG",
    "currency_name": "Netherlands Antillean guilder"
  },
  {
    "country_name": "Slovakia",
    "iso_country_code": "SK",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Slovenia",
    "iso_country_code": "SI",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Solomon Islands",
    "iso_country_code": "SB",
    "iso_currency_code": "SBD",
    "currency_name": "Solomon Islands dollar"
  },
  {
    "country_name": "Somalia",
    "iso_country_code": "SO",
    "iso_currency_code": "SOS",
    "currency_name": "Somali shilling"
  },
  {
    "country_name": "South Africa",
    "iso_country_code": "ZA",
    "iso_currency_code": "ZAR",
    "currency_name": "South African rand"
  },
  {
    "country_name": "South Georgia and the South Sandwich Islands",
    "iso_country_code": "GS",
    "iso_currency_code": "GBP",
    "currency_name": "British pound"
  },
  {
    "country_name": "South Sudan",
    "iso_country_code": "SS",
    "iso_currency_code": "SSP",
    "currency_name": "South Sudanese pound"
  },
  {
    "country_name": "Spain",
    "iso_country_code": "ES",
    "iso_currency_code": "EUR",
    "currency_name": "Euro"
  },
  {
    "country_name": "Sri Lanka",
    "iso_country_code": "LK",
    "iso_currency_code": "LKR",
    "currency_name": "Sri Lankan rupee"
  },
  {
    "country_name": "Sudan",
    "iso_country_code": "SD",
    "iso_currency_code": "SDG",
    "currency_name": "Sudanese pound"
  },
  {
    "country_name": "Suriname",
    "iso_country_code": "SR",
    "iso_currency_code": "SRD",
    "currency_name": "Surinamese dollar"
  },
  {
    "country_name": "Svalbard and Jan Mayen",
    "iso_country_code": "SJ",
    "iso_currency_code": "NOK",
    "currency_name": "Norwegian krone"
  },
  {
    "country_name": "Sweden",
    "iso_country_code": "SE",
    "iso_currency_code": "SEK",
    "currency_name": "Swedish krona"
  },
  {
    "country_name": "Switzerland",
    "iso_country_code": "CH",
    "iso_currency_code": "CHF",
    "currency_name": "Swiss franc"
  },
  {
    "country_name": "Syria",
    "iso_country_code": "SY",
    "iso_currency_code": "SYP",
    "currency_name": "Syrian pound"
  },
  {
    "country_name": "Taiwan",
    "iso_country_code": "TW",
    "iso_currency_code": "TWD",
    "currency_name": "New Taiwan dollar"
  },
  {
    "country_name": "Tajikistan",
    "iso_country_code": "TJ",
    "iso_currency_code": "TJS",
    "currency_name": "Tajikistani somoni"
  },
  {
    "country_name": "Tanzania",
    "iso_country_code": "TZ",
    "iso_currency_code": "TZS",
    "currency_name": "Tanzanian shilling"
  },
  {
    "country_name": "Thailand",
    "iso_country_code": "TH",
    "iso_currency_code": "THB",
    "currency_name": "Thai baht"
  },
  {
    "country_name": "Timor-Leste",
    "iso_country_code": "TL",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Togo",
    "iso_country_code": "TG",
    "iso_currency_code": "XOF",
    "currency_name": "West African CFA franc"
  },
  {
    "country_name": "Tokelau",
    "iso_country_code": "TK",
    "iso_currency_code": "NZD",
    "currency_name": "New Zealand dollar"
  },
  {
    "country_name": "Tonga",
    "iso_country_code": "TO",
    "iso_currency_code": "TOP",
    "currency_name": "Tongan paʻanga"
  },
  {
    "country_name": "Trinidad and Tobago",
    "iso_country_code": "TT",
    "iso_currency_code": "TTD",
    "currency_name": "Trinidad and Tobago dollar"
  },
  {
    "country_name": "Tunisia",
    "iso_country_code": "TN",
    "iso_currency_code": "TND",
    "currency_name": "Tunisian dinar"
  },
  {
    "country_name": "Turkey",
    "iso_country_code": "TR",
    "iso_currency_code": "TRY",
    "currency_name": "Turkish lira"
  },
  {
    "country_name": "Turkmenistan",
    "iso_country_code": "TM",
    "iso_currency_code": "TMT",
    "currency_name": "Turkmenistan manat"
  },
  {
    "country_name": "Turks and Caicos Islands",
    "iso_country_code": "TC",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Tuvalu",
    "iso_country_code": "TV",
    "iso_currency_code": "AUD",
    "currency_name": "Australian dollar"
  },
  {
    "country_name": "Uganda",
    "iso_country_code": "UG",
    "iso_currency_code": "UGX",
    "currency_name": "Ugandan shilling"
  },
  {
    "country_name": "Ukraine",
    "iso_country_code": "UA",
    "iso_currency_code": "UAH",
    "currency_name": "Ukrainian hryvnia"
  },
  {
    "country_name": "United Arab Emirates",
    "iso_country_code": "AE",
    "iso_currency_code": "AED",
    "currency_name": "United Arab Emirates dirham"
  },
  {
    "country_name": "United Kingdom",
    "iso_country_code": "GB",
    "iso_currency_code": "GBP",
    "currency_name": "British pound"
  },
  {
    "country_name": "United States",
    "iso_country_code": "US",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "United States Minor Outlying Islands",
    "iso_country_code": "UM",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Uruguay",
    "iso_country_code": "UY",
    "iso_currency_code": "UYU",
    "currency_name": "Uruguayan peso"
  },
  {
    "country_name": "Uzbekistan",
    "iso_country_code": "UZ",
    "iso_currency_code": "UZS",
    "currency_name": "Uzbekistani soʻm"
  },
  {
    "country_name": "Vanuatu",
    "iso_country_code": "VU",
    "iso_currency_code": "VUV",
    "currency_name": "Vanuatu vatu"
  },
  {
    "country_name": "Venezuela",
    "iso_country_code": "VE",
    "iso_currency_code": "VES",
    "currency_name": "Venezuelan bolívar soberano"
  },
  {
    "country_name": "Vietnam",
    "iso_country_code": "VN",
    "iso_currency_code": "VND",
    "currency_name": "Vietnamese đồng"
  },
  {
    "country_name": "Virgin Islands (British)",
    "iso_country_code": "VG",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Virgin Islands (U.S.)",
    "iso_country_code": "VI",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  },
  {
    "country_name": "Wallis and Futuna",
    "iso_country_code": "WF",
    "iso_currency_code": "XPF",
    "currency_name": "CFP franc"
  },
  {
    "country_name": "Western Sahara",
    "iso_country_code": "EH",
    "iso_currency_code": "MAD",
    "currency_name": "Moroccan dirham"
  },
  {
    "country_name": "Yemen",
    "iso_country_code": "YE",
    "iso_currency_code": "YER",
    "currency_name": "Yemeni rial"
  },
  {
    "country_name": "Zambia",
    "iso_country_code": "ZM",
    "iso_currency_code": "ZMW",
    "currency_name": "Zambian kwacha"
  },
  {
    "country_name": "Zimbabwe",
    "iso_country_code": "ZW",
    "iso_currency_code": "USD",
    "currency_name": "United States dollar"
  }
]

def generate_password(length=14):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def get_currency_map():
    try:
        r = requests.get(API_CURRENCIES, timeout=10)
        r.raise_for_status()
        return {item["alias"].upper(): str(item["code"]) for item in r.json()}
    except:
        return {}

def get_country_list():
    try:
        r = requests.get(API_COUNTRIES, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return []

def resolve_country(code, countries):
    code = code.upper()
    for c in countries:
        if c.get("currency", "").upper() == code:
            return str(c["id"]), c["title_en"]
    for entry in ISO_COUNTRY_TABLE:
        if code == entry["iso_currency_code"].upper():
            iso = entry["iso_country_code"]
            cname = entry["country_name"].lower()
            for c in countries:
                if c.get("alpha2", "").upper() == iso or c.get("title_en", "").lower() == cname:
                    return str(c["id"]), c.get("title_en")
    return None, None

def ask_user_for_country(code, countries, suggestion=None):
    win = tk.Toplevel()
    win.title(f"Выбор страны для {code}")
    win.geometry("500x400")
    selected = tk.StringVar()
    filter_var = tk.StringVar()

    ttk.Label(win, text=f"Валюта: {code}", font=("Arial", 12)).pack(pady=5)
    if suggestion:
        ttk.Label(win, text=f"Возможная страна: {suggestion}", foreground="gray").pack()

    entry = ttk.Entry(win, textvariable=filter_var)
    entry.pack(fill="x", padx=10, pady=5)
    listbox = tk.Listbox(win)
    listbox.pack(fill="both", expand=True, padx=10, pady=5)

    def refresh(*_):
        q = filter_var.get().lower()
        listbox.delete(0, tk.END)
        for c in countries:
            title = c.get("title_en", "")
            if q in title.lower():
                listbox.insert(tk.END, f"{title} (ID: {c['id']})")

    filter_var.trace_add("write", refresh)
    refresh()

    def choose():
        sel = listbox.curselection()
        if sel:
            val = listbox.get(sel[0])
            selected.set(val.split("ID:")[-1].strip(" )"))
            win.destroy()

    ttk.Button(win, text="Выбрать", command=choose).pack(pady=10)
    win.wait_window()

    cid = selected.get()
    for c in countries:
        if str(c["id"]) == cid:
            return cid, c["title_en"]
    return None, None

class CurrencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер валют с множеством сотрудников")
        self.root.geometry("900x670")

        self.name_var = tk.StringVar()
        self.file_var = tk.StringVar()

        self.currency_map = {}
        self.countries = get_country_list()
        self.to_register = []
        self.accounts = []

        ttk.Label(root, text="Сотрудники (через запятую):").pack(pady=(10, 0))
        ttk.Entry(root, textvariable=self.name_var, width=70).pack(pady=5)
        ttk.Label(root, text="Файл с валютами (.txt):").pack()
        ttk.Entry(root, textvariable=self.file_var, width=70).pack()
        ttk.Button(root, text="📂 Обзор...", command=self.select_file).pack(pady=4)
        ttk.Button(root, text="📧 Сгенерировать emailʼы", command=self.generate).pack(pady=5)

        self.text = tk.Text(root, height=20)
        self.text.pack(fill="both", padx=10, pady=10)

        self.btn_reg = ttk.Button(root, text="🚀 Зарегистрировать", command=self.register, state="disabled")
        self.btn_reg.pack()
        self.btn_save = ttk.Button(root, text="💾 Сохранить", command=self.save, state="disabled")
        self.btn_save.pack(pady=5)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.file_var.set(path)

    def generate(self):
        self.text.delete("1.0", tk.END)
        self.to_register.clear()

        raw = self.name_var.get().strip()
        employees = [x.strip() for x in raw.split(",") if x.strip()]
        if not employees:
            messagebox.showwarning("⚠", "Введите хотя бы одного сотрудника.")
            return

        try:
            with open(self.file_var.get(), encoding="utf-8") as f:
                used = [line.strip().upper() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Ошибка файла", str(e))
            return

        self.currency_map = get_currency_map()
        eur_count = used.count("EUR")
        used_codes = set(used) - {"EUR"}
        new_codes = sorted(set(self.currency_map.keys()) - used_codes - {"EUR"})

        # для каждого сотрудника — последовательно
        for staff in employees:
            for code in new_codes:
                email = f"{code}_AQ_{staff}_MB@test.acc"
                self.to_register.append((code, email))
                self.text.insert(tk.END, email + "\n")

            for i in range(eur_count):
                label = f"EUR ({i+1}/{eur_count}) [{staff}]" if eur_count > 1 else f"EUR [{staff}]"
                cid, cname = ask_user_for_country(label, self.countries)
                if not cname:
                    self.text.insert(tk.END, f"⛔ Пропущено: EUR → {staff} (страна не выбрана)\n")
                    continue
                email = f"EUR_AQ_{staff}_{cname}_MB@test.acc"
                self.to_register.append(("EUR", email))
                self.text.insert(tk.END, email + "\n")

        if self.to_register:
            self.btn_reg.config(state="normal")

    def register(self):
        self.accounts.clear()
        for code, email in self.to_register:
            currency_id = self.currency_map.get(code, "1")
            country_id, country_name = resolve_country(code, self.countries)
            if not country_id:
                hint = next((x["country_name"] for x in ISO_COUNTRY_TABLE if x["iso_currency_code"].upper() == code), None)
                country_id, country_name = ask_user_for_country(code, self.countries, hint)
                if not country_id:
                    self.text.insert(tk.END, f"⛔ Пропущено: {code} — страна не выбрана\n")
                    continue

            pwd = generate_password()

            payload = {
                "email_registration_form[email]": email,
                "email_registration_form[currencyId]": currency_id,
                "email_registration_form[plainPassword][first]": pwd,
                "email_registration_form[plainPassword][second]": pwd,
                "email_registration_form[country]": country_id,
                "first_refill_bonus_type_choice": "casino"
            }

            user_id = "-"
            try:
                res = requests.post(API_REGISTER, data=payload, timeout=10)
                res.raise_for_status()
                jwt = res.json().get("jwt")
                if jwt:
                    headers = {"Authorization": f"Bearer {jwt}"}
                    u = requests.get(API_USER, headers=headers, timeout=10)
                    if u.status_code == 200 and "id" in u.json():
                        user_id = str(u.json()["id"])
            except Exception as e:
                self.text.insert(tk.END, f"❌ Ошибка {code}: {e}\n")

            self.accounts.append({
                "currency": code,
                "email": email,
                "password": pwd,
                "country": country_name,
                "user_id": user_id
            })

            self.text.insert(tk.END, f"✅ {email} ({country_name}) → ID: {user_id}\n")

        if self.accounts:
            self.btn_save.config(state="normal")

    def save(self):
        def export(fmt):
            name = "accounts.csv" if fmt == "csv" else "accounts.txt"
            try:
                with open(name, "w", encoding="utf-8") as f:
                    if fmt == "csv":
                        f.write("Currency,Email,Password,Country,User ID\n")
                        for acc in self.accounts:
                            f.write(f"{acc['currency']},{acc['email']},{acc['password']},{acc['country']},{acc['user_id']}\n")
                    else:
                        for acc in self.accounts:
                            f.write(f"{acc['currency']}\n{acc['email']}\n{acc['password']}\n{acc['country']}\n{acc['user_id']}\n\n")
                messagebox.showinfo("Сохранено", f"Файл: {name}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        win = tk.Toplevel()
        win.title("Формат файла")
        fmt = tk.StringVar(value="txt")
        ttk.Label(win, text="Сохранить в формате:").pack(pady=10)
        ttk.Radiobutton(win, text="TXT", variable=fmt, value="txt").pack()
        ttk.Radiobutton(win, text="CSV", variable=fmt, value="csv").pack()
        ttk.Button(win, text="Сохранить", command=lambda: [win.destroy(), export(fmt.get())]).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyApp(root)
    root.mainloop()
