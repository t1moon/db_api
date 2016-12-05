# coding=utf-8

INSERT_THREAD = u'''INSERT INTO Threads
                   (forum, title, isClosed, user, date, message, slug, isDeleted)
                   VALUES
                   (%s, %s, %s, %s, %s, %s, %s, %s) ;
                '''

SELECT_THREAD_DATA_BY_ID = u'''SELECT date, dislikes, forum, id,
                                   isClosed, isDeleted, likes, message,
                                   likes - dislikes as points, posts,
                                   slug, title, user
                            FROM Threads
                            WHERE id = %s;
                        '''

SELECT_THREAD_BY_ID = u'''SELECT id
                            FROM Threads
                            WHERE id = %s ;
                        '''

SELECT_ALL_THREADS_BY_FORUM_UNSPECIFIED = u'''SELECT date, dislikes, forum,
                                                    id, isClosed, isDeleted,
                                                    likes, message,
                                                    likes - dislikes as points, posts,
                                                    slug, title, user
                                            FROM Threads
                                            WHERE forum = %s
                                            '''

UPDATE_THREAD_POSTS = u'''UPDATE Threads
                         SET posts = posts + %s
                         WHERE id = %s
                      '''

SELECT_THREAD_BY_POST_ID = u'''SELECT thread
                                   FROM Posts
                                   WHERE id = %s
                                '''
# переделать айдишник форума по slug айдишник юзера по email и оптимизировать это
SELECT_THREADS_BY_FORUM_OR_USER = u'''SELECT date, dislikes, forum_slug,
                                            id, isClosed, isDeleted,
                                            likes, message,
                                            likes - dislikes as points, posts,
                                            slug, title, user_email
                                     FROM thread
                                     WHERE {} = %s
                                  '''

SELECT_THREAD_DELETED_FLAG_BY_ID = u'''
                                SELECT isDeleted FROM Threads
                                WHERE id = %s
                            '''

UPDATE_THREAD_DELETED_FLAG = u'''UPDATE Threads
                                SET isDeleted = {}
                                WHERE id = %s;
                             '''

UPDATE_THREAD_POSTS_DELETED_FLAG = u'''UPDATE Posts
                                      SET isDeleted = {}
                                      WHERE thread = %s
                                   '''

UPDATE_THREAD_SET_IS_CLOSED_FLAG = u'''UPDATE Threads
                                       SET isClosed = {}
                                       WHERE id = %s;
                                    '''

UPDATE_THREAD = u'''UPDATE Threads
                    SET message = %s,
                        slug = %s
                    WHERE id = %s;
                 '''

UPDATE_THREAD_VOTES = u'''
                        UPDATE Threads
                        SET {} = {} + 1
                        WHERE id = %s ;
                        '''


INSERT_SUBSCRIPTION = u'''
                        INSERT INTO Subscriptions
                        (thread, user)
                        VALUES (%s, %s) ;
                    '''

DELETE_SUBSCRIPTION = u'''
                        DELETE FROM Subscriptions
                        WHERE thread = %s AND user = %s ;
                    '''