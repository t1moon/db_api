# coding=utf-8
SELECT_PROFILE_BY_EMAIL = u'''
                                SELECT id
                                FROM Users
                                WHERE email = %s
                                LIMIT 1;
                            '''

SELECT_PROFILE_NAME_ID_BY_EMAIL = u'''
                                SELECT name, id
                                FROM Users
                                WHERE email = %s
                                LIMIT 1;
                            '''

SELECT_FOLLOWERS_BY_EMAIL = u'''
                        SELECT follower
                        FROM Followers
                        WHERE followee = %s ;
                        '''

SELECT_FOLLOWINGS_BY_EMAIL = u'''
                        SELECT followee
                        FROM Followers
                        WHERE follower = %s ;
                        '''

SELECT_SUBSCRIPTIONS_BY_EMAIL = u'''
                                SELECT thread
                                FROM Subscriptions
                                WHERE user = %s ;
                            '''

SELECT_PROFILE_DATA_BY_EMAIL = '''
                            SELECT about, email, id, isAnonymous, name, username
                            FROM Users
                            WHERE email = %s ;
                         '''

INSERT_PROFILE = '''INSERT INTO Users
                  (username, about, name, email, isAnonymous)
                  VALUES
                  (%s, %s, %s, %s, %s);
               '''

INSERT_FOLLOWER = u'''INSERT INTO Followers
                     (follower, followee)
                     VALUES
                     (%s, %s) ;
                  '''

DELETE_FOLLOWER = u'''DELETE FROM Followers
                     WHERE follower = %s
                     AND followee = %s ;
                  '''

UPDATE_PROFILE = u'''
                UPDATE Users
                SET about = %s,
                     name = %s
                WHERE email = %s ;
              '''

UPDATE_USER_FORUM = u'''
                        UPDATE Users_Forum
                        SET user = %s, user_name = %s
                        WHERE user = %s ;
                    '''


SELECT_FOLLOW_RELATIONS = u'''SELECT Users.email
                                FROM Followers JOIN Users ON Users.email = {}
                                WHERE {} = %s
                            '''

SELECT_PROFILES_BY_FORUM_UNSPECIFIED = u'''SELECT (username, about, name, email, isAnonymous)
                                            FROM Users
                                            WHERE forum = %s
                            '''

SELECT_ALL_PROFILES_BY_FORUM_UNSPECIFIED = u'''SELECT user, user_name, user_id
                                                FROM Users_Forum
                                                WHERE forum = %s
                                            '''

INSERT_USER_FORUM = u'''INSERT INTO Users_Forum
                        (user, forum, user_name, user_id)
                        VALUES (%s, %s, %s, %s);
                    '''

# SELECT_USER_FOR_FORUM = u'''SELECT name
#                             FROM Users
#                             JOIN Forums
#                             ON Forums.user = Users.email
#                             WHERE Forums.user = %s
#                     '''

'''SELECT DISTINCT user_forum.user_email  FROM user_forum
INNER JOIN user ON user.email = user_forum.user_email
WHERE user_forum.short_name = forum1 ORDER BY user.name desc;

SELECT DISTINCT user_email, user_name  FROM user_forum
WHERE short_name = 'forumwithsufficientlylargename' ORDER BY user_name desc;'''