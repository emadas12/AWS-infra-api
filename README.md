# AWS-HomeWork
The partners in this assignement: Emad Asad,Rani Saed,Tofik Nassar
ecs - איך אנחנו מקבלים מידע על המצב של הקלאסטרים ב-AWS
המערכת מאפשרת לנו לבדוק איזה אשכולות (Clusters) פעילים כרגע ב-Amazon ECS. אנחנו מקבלים את הרשימה של כל האשכולות הפעילים, ואז מבקשים עוד מידע עליהם, כמו כמה משימות רצות כרגע, כמה מחכות בתור, וכמה שרתים מחוברים לכל אשכול. זה נותן לנו תמונה ברורה על מה קורה שם מאחורי הקלעים.

s3 - הצצה לכל הדליים של האחסון בענן
החלק הזה מאפשר לנו לראות איזה דליים (Buckets) יש לנו ב-Amazon S3. אנחנו מקבלים רשימה מסודרת של כל הדליים שקיימים בחשבון שלנו, כולל השמות שלהם ומתי הם נוצרו. ככה אפשר להבין מה קיים בענן ואיך הוא מאורגן.

ebs - לבדוק את האחסון על השרתים של AWS
כאן המערכת בודקת את כל כונני האחסון (Volumes) שמחוברים לשרתים שלנו ב-Amazon EBS. היא נותנת מידע כמו איזה כוננים מחוברים, מה הגודל שלהם, האם הם פעילים, והאם הם מוצפנים. זה ממש שימושי כדי לוודא שאין כוננים מיותרים שתופסים מקום או שהם לא מוגנים כמו שצריך.

auth - איך מתחברים בצורה בטוחה
לפני שאפשר לגשת לכל הנתונים האלה, צריך קודם כל להתחבר. כאן המשתמש מכניס את פרטי ההתחברות של AWS (המקשים הסודיים), ואז המערכת יוצרת לו Session זמני שמחזיק למשך שעה. זה אומר שאף אחד לא יכול לגשת לשירותים בלי לעבור דרך תהליך הזדהות מסודר.

session - ניהול ההתחברות בצורה חכמה
במקום לשמור את הסיסמאות עצמן (שזה לא מאובטח), המערכת יוצרת מזהה זמני (Session ID) ומאחסנת אותו יחד עם הנתונים של המשתמש לזמן קצוב. כל פעם שהמשתמש מבקש מידע, המערכת בודקת אם המזהה עדיין תקף. אם לא – הוא צריך להתחבר מחדש.

Flask - המנוע שמריץ את כל המערכת
הכל יושב על Flask, שזה כלי שעוזר לנו לבנות ממשק API בצורה פשוטה. כל בקשה (כמו "תראה לי את כל הדליים שלי ב-S3") מגיעה דרך נקודת גישה (Endpoint), והמערכת מחזירה תשובה מסודרת.

boto3 - הקשר הישיר עם AWS
הקוד משתמש בספרייה שנקראת Boto3, שהיא בעצם החוליה שמחברת בין פייתון לשירותים של AWS. דרכה אנחנו יכולים לשלוח בקשות ולקבל תשובות ישירות מ-AWS, במקום ללכת ללוח הבקרה שלהם ידנית.

jsonify - למה הכל בפורמט JSON?
כדי שיהיה קל לעבוד עם הנתונים, כל תשובה שאנחנו מחזירים מגיעה בפורמט JSON. זה פורמט מאוד נוח שניתן להשתמש בו בקלות באתרי אינטרנט, אפליקציות, ואפילו במסדי נתונים.

Flask Debug Mode - למה טוב שהמערכת רצה במצב דיבאג?
המערכת רצה עם debug=True, מה שאומר שכל שינוי בקוד מתעדכן ישר בלי שנצטרך להפעיל מחדש את השרת. זה חוסך הרבה כאב ראש כשעובדים על שיפורים ותיקונים.

סיכום
בקיצור, המערכת בודקת ומביאה מידע על ECS, S3, ו-EBS, ועושה את זה בצורה מסודרת דרך Flask ו-Boto3. בנוסף, יש לה מנגנון התחברות מאובטח, ככה שלא כל אחד יכול סתם להיכנס ולמשוך נתונים.
