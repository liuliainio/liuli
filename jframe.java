Spring,hibernate,Struts框架集成 2009-4-30 12:02 阅读(1)
赞评论转载分享复制地址编辑
上一篇  | 下一篇：spring总结
  
下面是这几天写的3个框架的集成，登陆页面，由于时间关系很多就没加注释了，总的来说我还是做了好久，因为导包的问题，可能代码有点多，以后有时间也要好好看看。



public class LoginAction extends Action {
private UserService userService;



//静态ActionForward


public void setUserService(UserService userService) {
  this.userService = userService;
}



public ActionForward execute(ActionMapping mapping, ActionForm form,
   HttpServletRequest request, HttpServletResponse response)
   throws Exception {

  LoginForm loginForm = (LoginForm)form;
  boolean b = this.userService.validate(loginForm.getUsername(),loginForm.getPassword());

  if(b){
   return mapping.findForward("success");
   
  }else{
  return mapping.findForward("fail");
  }
  
  

  
  
}



}


public class User {

private Integer id;
private String username;
private String password;
public Integer getId() {
  return id;
}
public void setId(Integer id) {
  this.id = id;
}
public String getUsername() {
  return username;
}
public void setUsername(String username) {
  this.username = username;
}
public String getPassword() {
  return password;
}
public void setPassword(String password) {
  this.password = password;
}




}

public interface UserDao {

public boolean checkUser(String name,String pass);


}


public class UserDaoImpl extends HibernateDaoSupport implements UserDao {



public boolean checkUser(final String name,  final String pass) {
  
   User user = (User) this.getHibernateTemplate().execute(
     
     
  new HibernateCallback(){
  
   public Object doInHibernate(Session session) throws HibernateException,SQLException {
    
    return session.createQuery("from User u where u.username=:name and u.password=:password")
      .setParameter("name", name)
      .setParameter("password", pass)
      
      .uniqueResult();
     
      
      
    
    
    
    
    
   }} );
  
   if(user!=null)return true;
    return false;
   }
  
  
  
  

  

  
  
}


public interface UserService {

public boolean validate(String name,String pass);



}


public class UserServiceImpl implements UserService{
private UserDao userDao;


public boolean validate(String name, String pass) {
  return this.userDao.checkUser(name, pass);
  
  
}

public void setUserDao(UserDao userDao) {
  this.userDao = userDao;
}





}


public class LoginForm extends ActionForm{
private String username;
private String password;




public String getUsername() {
  return username;
}


public void setUsername(String username) {
  this.username = username;
}

public String getPassword() {
  return password;
}






public void setPassword(String password) {
  this.password = password;
}










}

Hibernate映射文件
<hibernate-mapping>
<class name="com.lovo.action.User" table="T_user">
  
  <id name="id" type="integer">
  <column name="F_ID"></column>
  
  <generator class="native"></generator>
  
  </id>
  
  

  <property name="username" type="string" >
  <column name="F_username"></column>
  
  
  </property>
  
     
  <property name="password" type="string">
  <column name="F_password"></column>
  
  
  
  </property>
  
  

</class>

  
  
  

</hibernate-mapping>

Hibernate的配置文件

<hibernate-configuration>
<session-factory>

  <property name="connection.username">sa</property>
  <property name="connection.url">jdbc:jtds:sqlserver://127.0.0.1:1433/instant</property>
  <property name="connection.password"></property>
  <property name="connection.driver_class">net.sourceforge.jtds.jdbc.Driver</property>
   
  
  <!-- 添加方言适配器 -->
  <property name="dialect">org.hibernate.dialect.SQLServerDialect</property>
  
  
  <!--添加显示输出sql语句配置-->
  <property name="show_sql">true</property>
  <property name="format_sql">true</property>
  

  <!-- 自动提交 -->
  <property name="connection.autocommit">true</property>

  <!-- 加载配置文件 -->
  <mapping resource="com/lovo/action/User.hbm.xml"/>



</session-factory>




</hibernate-configuration>


Spring的配置文件

<beans>
<bean name="/login" class="com.lovo.action.LoginAction">
<property name="userService" ref="userService"></property>
</bean>
<bean id="userService" class="com.lovo.action.UserServiceImpl">

<property name="userDao" ref="userDao"></property>

</bean>


<bean id="userDao" class="com.lovo.action.UserDaoImpl">

<property name="hibernateTemplate" ref="hibernateTemplate"></property>

</bean>

<bean id="hibernateTemplate" class="org.springframework.orm.hibernate3.HibernateTemplate">

<property name="sessionFactory" ref="sfactory"></property>
</bean>

<bean id="sfactory" class="org.springframework.orm.hibernate3.LocalSessionFactoryBean">

<property name="configLocation" value="classpath:hibernate.cfg.xml"></property>

</bean>



</beans>

struts的配置文件

<struts-config>
  
  <form-beans>
   <form-bean name="loginForm" type="com.lovo.bean.LoginForm">
  
   
  </form-bean>
  
  </form-beans>
<action-mappings>


<action path="/login"
   name="loginForm"
   type="com.lovo.action.LoginAction"
   validate="true"
   input="/login.jsp"
  
>
   <forward name="success" path="/success.jsp"></forward>
   <forward name="fail" path="/fail.jsp"></forward>


</action>




</action-mappings>
  
  
<controller processorClass="org.springframework.web.struts.DelegatingRequestProcessor"></controller>

  
  
</struts-config>

servlet配置文件
<web-app xmlns="http://java.sun.com/xml/ns/j2ee" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.4" xsi:schemaLocation="http://java.sun.com/xml/ns/j2ee   http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd">
   <!--配置全局初始化参数-->
  <context-param>
    <param-name>contextConfigLocation</param-name>
    <param-value>/WEB-INF/classes/cc.xml</param-value>
  </context-param>
  <listener>
    <listener-class>org.springframework.web.context.ContextLoaderListener</listener-class>
  </listener>
  
  <servlet>
    <servlet-name>action</servlet-name>
    <servlet-class>org.apache.struts.action.ActionServlet</servlet-class>
    <init-param>
      <param-name>config</param-name>
      <param-value>/WEB-INF/struts-config.xml</param-value>
    </init-param>
    <init-param>

    </init-param>
    <load-on-startup>0</load-on-startup>
  </servlet>
  <servlet>
    <servlet-name>action_tmp</servlet-name>
    <servlet-class>org.apache.struts.action.ActionServlet</servlet-class>
   
  
  <servlet-mapping>
    <servlet-name>action</servlet-name>
    <url-pattern>*.do</url-pattern>
  </servlet-mapping>
  <welcome-file-list>
    <welcome-file>login.jsp</welcome-file>
  </welcome-file-list>
</web-app>
登陆页面（login.jsp）

    <html:form action="login.do" method="post"> 
     name:<html:text property="username"/><br>
     pass:<html:password property="password"/><br>
      <html:submit value="login"></html:submit><br>
    
    </html:form>
    
    
   
其他的就不说了，导包，还有成功和失败页面，数据库还要建表
