# news_api — NewsHubs4BD অ্যাপের সব লিংক

NewsHubs4BD অ্যাপের সব তালিকা এই repo-তে থাকে এবং
`https://zahirul064.github.io/news_api/` থেকে অ্যাপে যায়।
**এখানে লিংক বদলালে অ্যাপ আপডেট করতে হয় না।** GitHub-এ সেভ (commit) করার
১–২ মিনিট পর অ্যাপে **টেনে রিফ্রেশ** করলেই নতুন লিংক চলে আসে। অ্যাপ ১৫ মিনিটের
বেশি বন্ধ থাকার পর খুললে নিজে থেকেও রিফ্রেশ হয়।

## কোন ফাইলে কী

| ফাইল | অ্যাপের কোথায় |
|---|---|
| `news_category.json` | হোমের ক্যাটাগরি কার্ডগুলো (নতুন ক্যাটাগরিও এখানে যোগ হয়) |
| `bd_national_news.json` | জাতীয় বাংলা পত্রিকা |
| `eng_national_news.json` | ইংরেজি পত্রিকা |
| `online_news.json` | অনলাইন নিউজ |
| `international_news.json` | আন্তর্জাতিক খবর |
| `bd_media_news.json` | টিভি / মিডিয়া |
| `bd_local_news.json`, `district_news.json` | ৬৪ জেলার স্থানীয় খবর |
| `islamic_magazine.json` | ইসলামী ম্যাগাজিন |
| `tech_magazine.json` | টেক / আইটি ম্যাগাজিন |
| `kids_science_magazine.json` | শিশু-কিশোর ও বিজ্ঞান |
| `literature_culture_magazine.json` | সাহিত্য ও সংস্কৃতি |
| `top_outlets.json` | হোমের "Top Outlets" সারি (১০টি লোগো) |
| `app_version.json` | নতুন সংস্করণের ব্যানার |
| `trending.json` | ট্রেন্ডিং খবর — **হাতে বদলাবেন না**, প্রতি ৩০ মিনিটে নিজে তৈরি হয় |

## নতুন পত্রিকা যোগ করা (যেমন ইংরেজি পত্রিকায়)

`eng_national_news.json` খুলে ✏️ (Edit) চাপুন, শেষ `}` এর পরে একটা কমা দিয়ে এটা বসান:

```json
  {
    "title": "পত্রিকার নাম",
    "imgUrl": "https://লোগোর-লিংক.png",
    "pdfUrl": "https://পত্রিকার-ওয়েবসাইট.com/"
  }
```

- `imgUrl` না জানলে `""` রেখে দিন — অ্যাপ ওয়েবসাইটের আইকন নিজে খুঁজে নেবে।
- উপরে রাখলে তালিকায় আগে দেখাবে।
- তারপর **Commit changes** চাপুন।

## নতুন ক্যাটাগরি যোগ করা

1. নতুন একটা ফাইল বানান, যেমন `sports_magazine.json`, ভেতরে পত্রিকার তালিকা (উপরের নিয়মে)।
2. `news_category.json`-এর শেষে একটা ঘর যোগ করুন:

```json
    {
        "imageUrl": "",
        "cat_title": "Sports Magazine",
        "cat_title_bn": "খেলার ম্যাগাজিন",
        "cat_subtitle": "খেলার ম্যাগাজিন",
        "serverUrl": "https://zahirul064.github.io/news_api/sports_magazine.json",
        "icon": "sports",
        "colors": ["#0B6E44", "#22A06B"]
    }
```

- `icon` যা দেওয়া যায়: `newspaper` `translate` `bolt` `world` `tv` `city` `mosque` `quran`
  `tech` `computer` `science` `kids` `book` `palette` `sports` `business` `health`
  `education` `music` `feed`
- `colors`: কার্ডের দুই রঙ (হেক্স কোড)। না দিলে অ্যাপ নিজে একটা রঙ বেছে নেয়।
- `count` লিখতে হবে না — পরীক্ষা নিজে বসিয়ে দেয়।

## Top Outlets বদলানো

`top_outlets.json`-এ প্রতিটি ঘর:

```json
  { "name": "Prothom Alo", "name_bn": "প্রথম আলো", "url": "https://www.prothomalo.com", "initials": "PA", "logo": "" }
```

যতগুলো রাখবেন অ্যাপে ততগুলোই দেখাবে, একই ক্রমে।

## ভুল হলে কী হয়

- প্রতিবার সেভ করার পর **"Check lists & update counts"** নামে একটা পরীক্ষা চলে
  (Actions ট্যাবে দেখা যায়)। কমা/বন্ধনী ভুল, খালি নাম, `https://` ছাড়া লিংক বা একই
  লিংক দুবার থাকলে সেটা লাল ❌ হয় আর GitHub আপনাকে ইমেইল করে — কোন ফাইলের কোন
  ঘরে ভুল তা সেখানে লেখা থাকে।
- ভুল ঠিক না হওয়া পর্যন্ত অ্যাপ আগের ঠিক তালিকাটাই দেখায় — অ্যাপ ভাঙে না।
- একই পরীক্ষা হোমের ক্যাটাগরি কার্ডে পত্রিকার সংখ্যাও নিজে থেকে হালনাগাদ করে।

## অফলাইন

অ্যাপ প্রতিটি তালিকার শেষ ঠিক কপি ফোনে রেখে দেয়। ইন্টারনেট না থাকলে সেটাই দেখায়
এবং হোমে "ইন্টারনেট নেই — শেষবার সংরক্ষিত তালিকা দেখাচ্ছে" লেখা আসে।

বাদ দেওয়া লিংক ও কারণ: [`REMOVED_URLS.md`](REMOVED_URLS.md)
